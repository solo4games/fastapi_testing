import shutil
import os.path

from fastapi import UploadFile, status, HTTPException
from sqlalchemy import select

from app.dao.dao import BaseDAO
from app.documents.models import Documents, DocumentsText


class DocumentDAO(BaseDAO):
    model = Documents

    @classmethod
    def parse_document_path(cls, file: UploadFile) -> str:
        path = "app/static/images/" + file.filename
        if os.path.isfile(path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File Already Exists")
        with open(path, "wb+") as f:
            shutil.copyfileobj(file.file, f)
        if not os.path.isfile(path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        return path


class DocumentTextDAO(BaseDAO):
    model = DocumentsText

    async def find_document_text(self, file_id: int):
        query = select(self.model).filter_by(id_doc=file_id)
        result = await self.session.execute(query)
        return result.first()

