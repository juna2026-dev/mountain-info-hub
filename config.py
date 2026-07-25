from dataclasses import dataclass


@dataclass(frozen=True)
class RssSource:
    name: str
    url: str
    category: str  # "it" or "mountain"


RSS_SOURCES: list[RssSource] = [
    RssSource(name="Zenn", url="https://zenn.dev/feed", category="it"),
    RssSource(
        name="Qiita",
        url="https://qiita.com/popular-items/feed.atom",
        category="it",
    ),
    RssSource(
        name="はてなブックマーク",
        url="https://b.hatena.ne.jp/hotentry/it.rss",
        category="it",
    ),
    RssSource(
        name="Googleニュース(登山)",
        url="https://news.google.com/rss/search?q=%E7%99%BB%E5%B1%B1&hl=ja&gl=JP&ceid=JP:ja",
        category="mountain",
    ),
]


@dataclass(frozen=True)
class DangerLink:
    name: str
    url: str
    category: str  # "bear" / "accident" / "lightning"
    area: str


DANGER_LINKS: list[DangerLink] = [
    DangerLink(
        name="長野県 ツキノワグマ情報マップ",
        url="https://www.pref.nagano.lg.jp/shinrin/sangyo/ringyo/choju/joho/kuma-map.html",
        category="bear",
        area="長野県",
    ),
    DangerLink(
        name="気象庁 雷ナウキャスト",
        url="https://www.jma.go.jp/bosai/nowc/",
        category="lightning",
        area="全国",
    ),
]


@dataclass(frozen=True)
class OnsenLink:
    name: str
    url: str
    area: str  # 最寄りの山域


ONSEN_LINKS: list[OnsenLink] = [
    OnsenLink(
        name="大町温泉郷観光協会(公式)",
        url="https://www.omachionsen.jp/",
        area="北アルプス(扇沢・黒部ダム方面)",
    ),
    OnsenLink(
        name="中の湯温泉旅館(公式・上高地エリア通年営業)",
        url="https://nakanoyu-onsen.jp/",
        area="北アルプス(上高地・穂高方面)",
    ),
    OnsenLink(
        name="全国の温泉を検索(楽天トラベル)",
        url="https://travel.rakuten.co.jp/onsen/",
        area="全国",
    ),
]

DATABASE_URL = "sqlite:///./data/app.db"
FETCH_INTERVAL_MINUTES = 30


@dataclass(frozen=True)
class TrailheadLinkSite:
    name: str
    url: str
    note: str


# ② 全国の登山口情報を網羅する外部サイトへのリンク
TRAILHEAD_LINK_SITES: list[TrailheadLinkSite] = [
    TrailheadLinkSite(
        name="登山口ナビ",
        url="https://tozanguchinavi.com/",
        note="約1700ヶ所の登山口を掲載。駐車場の混雑情報の更新頻度が高い",
    ),
    TrailheadLinkSite(
        name="登山口P",
        url="https://tozanguchi-p.com/",
        note="駐車場の写真・トイレ有無・マップコード情報が充実",
    ),
    TrailheadLinkSite(
        name="登山口.com",
        url="https://www.tozanguchi.com/",
        note="駐車場・マップコード・近隣温泉情報までセットで掲載",
    ),
]


@dataclass(frozen=True)
class TrailheadSpot:
    name: str
    address: str  # カーナビ入力用の住所
    area: str
    parking_capacity: str
    source_url: str


# ③ 個別登山口情報(今後少しずつ追加していく)
TRAILHEAD_SPOTS: list[TrailheadSpot] = [
    TrailheadSpot(
        name="三股登山口駐車場",
        address="長野県安曇野市穂高有明7899",
        area="北アルプス(常念岳・蝶ヶ岳方面)",
        parking_capacity="約200台",
        source_url="https://mt-parking-info.azumino-e-tabi.net/detail/mitsumata.php",
    ),
]
