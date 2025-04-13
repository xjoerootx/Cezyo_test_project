"""Модуль для настройки подключения к базе данных.

Создает SQLAlchemy engine и sessionmaker, а также определяет функцию
get_db для получения сессии БД.
"""

import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL is None:
    raise Exception('DATABASE_URL не установлен. Проверьте файл .env')

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Возвращает сессию БД для зависимостей FastAPI.

    Гарантирует закрытие сессии после использования.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
