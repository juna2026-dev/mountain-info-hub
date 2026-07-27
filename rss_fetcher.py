import re
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
import time
from time import mktime

import feedparser
import requests
from sqlmodel import Session, select

# Googleニュース等がボットとして判定しないよう、一般的なブラウザのUser-Agentを送信する
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

from config import ARTICLE_RETENTION_DAYS, RSS_SOURCES, RssSource
from database import engine
from models import Article

# タイトル類似度がこの値以上なら「同じニュース」とみなす(0.0〜1.0)
TITLE_SIMILARITY_THRESHOLD = 0.85

# 直近何時間以内の記事だけを重複判定の対象にするか
DEDUP_WINDOW_HOURS = 72


def _normalize_title(title: str) -> str:
    """メディア名の付記(【】や - 区切りの末尾など)を取り除き、比較しやすくする。"""
    title = re.sub(r"\s*[-|｜]\s*[^-|｜]+$", "", title)  # 末尾の "- メディア名" を除去
    title = re.sub(r"[【】\[\]()（）]", "", title)
    return title.strip()


def _is_duplicate_title(title: str, recent_titles: list[str]) -> bool:
    """正規化したタイトルを、直近記事のタイトル群と比較し類似判定する。"""
    normalized = _normalize_title(title)
    for existing in recent_titles:
        ratio = SequenceMatcher(None, normalized, _normalize_title(existing)).ratio()
        if ratio >= TITLE_SIMILARITY_THRESHOLD:
            return True
    return False


def _parse_published_at(entry) -> datetime | None:
    """RSSエントリの公開日時をdatetimeに変換する。取得できなければNone。"""
    time_struct = entry.get("published_parsed") or entry.get("updated_parsed")
    if time_struct is None:
        return None
    return datetime.fromtimestamp(mktime(time_struct), tz=timezone.utc)


def fetch_source(source: RssSource, session: Session, recent_titles: list[str]) -> int:
    """1つのRSSソースを取得し、新規かつ非重複の記事だけをDBに保存する。保存件数を返す。"""
    response = None
    last_error = None
    for attempt in range(3):
        try:
            response = requests.get(source.url, headers=REQUEST_HEADERS, timeout=10)
            response.raise_for_status()
            break
        except requests.RequestException as e:
            last_error = e
            response = None
            time.sleep(2 * (attempt + 1))  # 2秒, 4秒, 6秒と間隔を空けて再試行

    if response is None:
        print(f"[warn] failed to request feed after retries: {source.name} ({last_error})")
        return 0

    parsed = feedparser.parse(response.content)

    if parsed.bozo:
        print(f"[warn] failed to parse feed: {source.name} ({parsed.bozo_exception})")
        print(f"[debug] status_code={response.status_code}")
        print(f"[debug] response_snippet={response.text[:300]!r}")
        return 0

    saved_count = 0
    for entry in parsed.entries:
        url = entry.get("link")
        title = entry.get("title")
        if not url or not title:
            continue

        existing = session.exec(select(Article).where(Article.url == url)).first()
        if existing:
            continue

        if _is_duplicate_title(title, recent_titles):
            continue

        article = Article(
            title=title,
            url=url,
            source=source.name,
            category=source.category,
            published_at=_parse_published_at(entry),
        )
        session.add(article)
        recent_titles.append(title)  # 同一取得内での重複も防ぐため即座に追加
        saved_count += 1

    session.commit()
    return saved_count


def cleanup_old_articles() -> int:
    """保持期間(ARTICLE_RETENTION_DAYS)より古い記事をDBから削除する。削除件数を返す。"""
    with Session(engine) as session:
        cutoff = datetime.now(timezone.utc) - timedelta(days=ARTICLE_RETENTION_DAYS)
        old_articles = session.exec(
            select(Article).where(Article.fetched_at < cutoff)
        ).all()
        for article in old_articles:
            session.delete(article)
        session.commit()
        return len(old_articles)


def fetch_all_sources() -> None:
    """全RSSソースを取得してDBに保存する(重複タイトルは除外)。"""
    with Session(engine) as session:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=DEDUP_WINDOW_HOURS)
        recent_titles = list(
            session.exec(
                select(Article.title).where(Article.fetched_at >= cutoff)
            ).all()
        )

        total = 0
        for source in RSS_SOURCES:
            count = fetch_source(source, session, recent_titles)
            total += count
            print(f"[info] {source.name}: {count} new articles")
        print(f"[info] total new articles: {total}")

    deleted_count = cleanup_old_articles()
    print(f"[info] deleted {deleted_count} old articles (older than {ARTICLE_RETENTION_DAYS} days)")
