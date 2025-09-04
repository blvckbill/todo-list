import re
from todolist import config

from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase, declared_attr

def create_db_engine(connection_string: str):
    """Create a database engine with proper timeout settings.

    Args:
        connection_string: Database connection string
    """

    url = make_url(connection_string)

    #custom connection settings for database cinnection pool
    timeout_kwargs = {
        "pool_size" : config.DATABASE_ENGINE_POOL_SIZE,
        "max_overflow" : config.DATABASE_ENGINE_MAX_OVERFLOW,
        "pool_recycle" : config.DATABASE_ENGINE_POOL_RECYCLE,
        "pool_timeout" : config.DATABASE_ENGINE_POOL_TIMEOUT,
        "pool_pre_ping" : config.DATABASE_ENGINE_POOL_PING
    }

    return create_engine(url, **timeout_kwargs)

#create database engine with standard timeout
engine = create_db_engine(
    config.SQLALCHEMY_DATABASE_URI
)

SessionLocal = sessionmaker(bind=engine)

def resolve_table_name(name):
    """Resolve table names for their mapped names"""
    names = re.split("?=[A-Z]", name)
    return "_".join([x.lower() for x in names if x])
    


class Base(DeclarativeBase):
    """Base class for all SQLALchemy models"""
    __repr_attrs__ = []
    __repr_max_length__ = 15

    @declared_attr.directive
    def __tablename__(cls):
        return resolve_table_name(cls.__name__)

