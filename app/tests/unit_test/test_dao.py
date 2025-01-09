import os
from unittest.mock import patch

import pytest
from fastapi import UploadFile, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.documents.dao import DocumentDAO
from app.documents.models import Documents, DocumentsText
from app.tests.conftest import async_db_session
from app.tasks.tasks import analyze_document_task


async def test_find_one_or_none(async_db_session: AsyncSession):

    document_dao = DocumentDAO(async_db_session)
    test_result = await document_dao.find_one_or_none(id=1)

    select_result = await async_db_session.execute(select(Documents).where(Documents.id == 1))

    assert test_result == select_result.scalar_one_or_none()

async def test_parse_document_positive(async_db_session: AsyncSession):
    document_dao = DocumentDAO(async_db_session)
    test_file_path = 'app/tests/static/test_image.png'

    with open(test_file_path, 'rb+') as file:
        new_file_bytes = UploadFile(filename="test_image.png", file=file)
        path_for_test = document_dao.parse_document_path(new_file_bytes)

    assert path_for_test == 'app/static/images/test_image.png'

    assert os.path.isfile(path_for_test)

    os.remove(path_for_test)

@patch('os.path.isfile')
@pytest.mark.parametrize("mock_return, status_code, detail", [(False, 404, 'File not found'),
                                                              (True, 404, 'File Already Exists')])
async def test_parse_document_negative(mock_is_file, async_db_session: AsyncSession, mock_return, status_code, detail):
    document_dao = DocumentDAO(async_db_session)
    test_file_path = 'app/tests/static/test_image.png'

    mock_is_file.side_effect = [mock_return, mock_return]
    with open(test_file_path, 'rb+') as file:
        new_file_bytes = UploadFile(filename="test_image.png", file=file)
        with pytest.raises(HTTPException) as exc_info:
            document_dao.parse_document_path(new_file_bytes)

    assert exc_info.value.status_code == status_code
    assert exc_info.value.detail == detail

    if not mock_return:
        os.remove('app/static/images/test_image.png')

async def test_analyze_task():
    text = analyze_document_task('app/tests/static/image_for_analyzing.png')

    assert "HELLO" in text

@patch('os.path.isfile', return_value=False)
async def test_analyze_task_negative(mock_is_file):
    with pytest.raises(HTTPException) as exc_info:
        analyze_document_task('app/tests/static/image_for_analyzing.png')

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == 'Document image not found'
