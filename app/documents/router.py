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
    """
        Загрузка документа на сервер.

        Этот эндпоинт позволяет пользователям загружать файл документа, который
        сохраняется в указанном пути и записывается в базу данных.

        Аргументы:
            file (UploadFile): Загружаемый файл.
            session (AsyncSession): Зависимость для работы с базой данных.

        Возвращает:
            JSONResponse: Сообщение об успешной загрузке с ID документа, если загрузка прошла успешно.

        Возможные статус-коды:
            - 201 Created: Документ успешно загружен.
            - 500 Internal Server Error: Ошибка при обработке файла или сохранении в базе данных.
    """

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
    """
        Удаление документа по его ID.

        Этот эндпоинт удаляет документ из базы данных и удаляет
        соответствующий файл из файловой системы.

        Аргументы:
            file_id (int): ID документа, который нужно удалить.
            session (AsyncSession): Зависимость для работы с базой данных.

        Возвращает:
            JSONResponse: Сообщение об успешном удалении документа.

        Возможные статус-коды:
            - 200 OK: Документ успешно удалён.
            - 500 Internal Server Error: Ошибка при удалении файла или сохранении изменений в базе данных.
    """

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
    """
      Анализ документа по его ID.

      Этот эндпоинт выполняет анализ содержимого документа и сохраняет
      результаты анализа в базе данных.

      Аргументы:
          file_id (int): ID документа, который нужно проанализировать.
          session (AsyncSession): Зависимость для работы с базой данных.

      Возвращает:
          JSONResponse: Сообщение об успешном выполнении анализа.

      Возможные статус-коды:
          - 200 OK: Анализ успешно завершён.
          - 404 Not Found: Документ с указанным ID не найден.
          - 500 Internal Server Error: Ошибка при сохранении результатов анализа в базе данных.
    """

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
    """
    Получение текста анализа документа по его ID.

    Этот эндпоинт извлекает текст анализа документа из базы данных.

    Аргументы:
        file_id (int): ID документа, текст которого нужно получить.
        session (AsyncSession): Зависимость для работы с базой данных.

    Возвращает:
        JSONResponse: Текст анализа документа.

    Возможные статус-коды:
        - 200 OK: Текст успешно получен.
        - 404 Not Found: Текст анализа документа не найден.
    """

    document_text_dao = DocumentTextDAO(session)
    text = await document_text_dao.find_one_or_none(id_doc=file_id)
    if not text:
        raise HTTPException(status_code=404, detail="Document text not found")
    return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"text": text.text})