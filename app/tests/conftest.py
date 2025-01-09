import json

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import insert

from app.main import app as fastapi_app
from app.database import Base, async_session_maker, async_engine, get_session
from app.documents.models import Documents, DocumentsText
from app.config import settings


@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    assert settings.MODE == "TEST"

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    def open_mock_json(model: str):
        with open(f"app/tests/mock_{model}.json", "r") as f:
            return json.load(f)

    documents = open_mock_json("documents")
    documents_text = open_mock_json("documents_text")

    async with async_session_maker() as session:
        add_documents = insert(Documents).values(documents)
        add_documents_text = insert(DocumentsText).values(documents_text)

        await session.execute(add_documents)
        await session.execute(add_documents_text)

        await session.commit()


@pytest.fixture
async def async_db_session():
    async with async_session_maker() as session:
        yield session


@pytest.fixture(scope="function", autouse=True)
async def client(async_db_session):

    def override():
        yield async_db_session

    fastapi_app.dependency_overrides[get_session] = override

    async with AsyncClient(transport=ASGITransport(fastapi_app), base_url="http://test") as client:
        yield client