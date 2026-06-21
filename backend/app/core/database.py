from sqlalchemy import create_engine, inspect, Engine
from functools import lru_cache
from .config import get_settings


@lru_cache()
def get_engine() -> Engine:
    settings = get_settings()
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
    )
    return engine


def get_inspector():
    return inspect(get_engine())
