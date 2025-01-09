import os

from fastapi import APIRouter, HTTPException, Depends
from fastapi import UploadFile, status
from sqlalchemy import delete

from app.documents.dao import DocumentDAO, DocumentTextDAO
from app.database import async_session_maker, get_session
from app.documents.models import Documents, DocumentsText
from app.tasks.tasks import analyze_document_task
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse

router = APIRouter(tags=["Documents"])

@router.post("/upload_doc")
async def upload_document(file: UploadFile, session: AsyncSession = Depends(get_session)) -> JSONResponse:
    path = DocumentDAO.parse_document_path(file)
    doc_obj = Documents(path=path)
    session.add(doc_obj)
    try:
        await session.commit()
        return JSONResponse(status_code=status.HTTP_201_CREATED,
                            content={"message": f"Document uploaded successfully with id - {doc_obj.id}"})
    except SQLAlchemyError as e:
        os.remove(path)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))

@router.delete("/doc_delete")
async def delete_document(file_id: int, session: AsyncSession = Depends(get_session)) -> JSONResponse:
    query = delete(Documents).where(Documents.id == file_id).returning(Documents.path)
    deleted_document = await session.execute(query)
    path = deleted_document.fetchone().path
    if os.path.exists(path):
        os.remove(path)
    try:
        await session.commit()
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": "Document deleted successfully"})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/doc_analyze")
async def analyze_document(file_id: int, session: AsyncSession = Depends(get_session)) -> JSONResponse:
    document_dao = DocumentDAO(session)

    doc = await document_dao.find_one_or_none(id=file_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    text = analyze_document_task.delay(doc.path).get()
    doc_text = DocumentsText(id_doc=doc.id, text=text)
    session.add(doc_text)

    try:
        await session.commit()
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": "Analyzing of document succeeded"})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_text")
async def get_text(file_id: int, session: AsyncSession = Depends(get_session)) -> JSONResponse:
    document_text_dao = DocumentTextDAO(session)
    text = await document_text_dao.find_one_or_none(id_doc=file_id)
    if not text:
        raise HTTPException(status_code=404, detail="Document text not found")
    return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"text": text.text})