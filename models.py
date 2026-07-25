from datetime import datetime

from sqlmodel import Field, SQLModel


class Article(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    url: str = Field(unique=True, index=True)
    source: str
    category: str = Field(index=True)
    published_at: datetime | None = None
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
