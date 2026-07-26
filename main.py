from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from auth import verify_credentials
from config import DANGER_LINKS, ONSEN_LINKS, TRAILHEAD_LINK_SITES, TRAILHEAD_SPOTS
from database import engine, init_db
from models import Article
from rss_fetcher import fetch_all_sources
from scheduler import start_scheduler, stop_scheduler

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    fetch_all_sources()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_root(request: Request, username: str = Depends(verify_credentials)):
    with Session(engine) as session:
        articles = session.exec(
            select(Article)
            .order_by(
                Article.published_at.is_(None),
                Article.published_at.desc(),
            )
            .limit(100)
        ).all()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "articles": articles,
            "danger_links": DANGER_LINKS,
            "onsen_links": ONSEN_LINKS,
            "trailhead_link_sites": TRAILHEAD_LINK_SITES,
            "trailhead_spots": TRAILHEAD_SPOTS,
        },
    )


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
