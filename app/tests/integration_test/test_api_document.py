import os
import shutil

from httpx import AsyncClient
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.documents.models import Documents, DocumentsText


@pytest.mark.parametrize('file_id, status_code, text_document', [(2, 200, "text from image2"),
                                                  (3, 200, "text from image3"),])
async def test_getting_text(client: AsyncClient, file_id: int, status_code: int, text_document: str):
    response = await client.get("/get_text", params={"file_id" : file_id})
    assert response.status_code == status_code
    assert response.json()["text"] == text_document

async def test_getting_text_negative(client: AsyncClient):
    response = await client.get("/get_text", params={"file_id" : 777})
    assert response.status_code == 404
    assert response.json()["detail"] == "Document text not found"

async def test_uploading_image(client: AsyncClient, async_db_session: AsyncSession):
    with open('app/tests/static/test_image.png', 'rb+') as image_file:
        response = await client.post("/upload_doc", files={"file": image_file})

    print(response.json())
    assert response.status_code == 201

    file_path = 'app/static/images/test_image.png'
    assert os.path.isfile(file_path) == True

    query = select(Documents).where(Documents.path == file_path)
    result = await async_db_session.execute(query)
    assert result.first() is not None

    os.remove(file_path)

async def test_deleting_image(client: AsyncClient, async_db_session: AsyncSession):
    test_file_path = 'app/tests/static/image_for_deleting.png'
    base_file_path = 'app/tests/static/test_image.png'

    shutil.copyfile(base_file_path, test_file_path)

    response = await client.delete("/doc_delete", params={"file_id" : 5})

    assert response.status_code == 200
    assert response.json()["message"] == "Document deleted successfully"

    result = await async_db_session.execute(select(Documents).where(Documents.path == test_file_path))
    assert result.first() is None

    assert os.path.exists(test_file_path) == False

async def test_analyze_document(client: AsyncClient, async_db_session: AsyncSession):
    response = await client.post("/doc_analyze", params={"file_id" : 1})

    assert response.status_code == 200
    assert response.json()["message"] == "Analyzing of document succeeded"

    result = await async_db_session.scalars(select(DocumentsText).where(DocumentsText.id_doc == 1))
    text_res = result.first()
    assert text_res is not None

    assert "HELLO" in text_res.text

async def test_analyze_document_negative(client: AsyncClient, async_db_session: AsyncSession):
    response = await client.post("/doc_analyze", params={"file_id": 123})

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"
