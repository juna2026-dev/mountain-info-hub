from datetime import datetime

from sqlalchemy import Column, String
from sqlmodel import Field, SQLModel


class Article(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(sa_column=Column(String(512)))
    url: str = Field(sa_column=Column(String(512), unique=True, index=True))
    source: str
    category: str = Field(index=True)
    published_at: datetime | None = None
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
