from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine

load_dotenv()

from config import DATABASE_URL
# Article などのモデルを読み込ませることで、
# SQLModel.metadata にテーブル定義を登録する(副作用目的のimport)
import models  # noqa: F401

import os

os.makedirs("data", exist_ok=True)

engine = create_engine(DATABASE_URL, echo=False)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
