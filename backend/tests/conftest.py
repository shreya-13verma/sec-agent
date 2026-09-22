"""Test configuration and fixtures using TestClient."""
import pytest
from starlette.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from backend.app.core.database import Base, get_db
from backend.app.main import app

SYNC_TEST_DB_URL = "sqlite:///./test_sync.db"
ASYNC_TEST_DB_URL = "sqlite+aiosqlite:///./test_async.db"

@pytest.fixture(scope="function")
def test_client():
    async_engine = create_async_engine(ASYNC_TEST_DB_URL, echo=False)
    async_session = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

    # Init tables
    import asyncio
    async def init():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    asyncio.run(init())

    async def override_get_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

    async def teardown():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await async_engine.dispose()
    asyncio.run(teardown())
