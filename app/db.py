from geoalchemy2 import Geometry
from sqlalchemy import (
    Table,
    Column,
    MetaData,
    Integer,
    String,
    Float,
)
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine

metadata = MetaData()

fields = Table(
    'fields',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('crop', String, nullable=True),
    Column('productivity', Float, nullable=True),
    Column('area', Float),
    Column('region', String, nullable=True),
    Column('geometry', Geometry(from_text='ST_GeomFromGeoJSON')),
)


def init_db() -> AsyncEngine:
    return create_async_engine(
        'postgresql+asyncpg://postgres:postgres@geoapi-postgres-service/postgres'
    )
