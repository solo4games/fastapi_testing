import shutil
import os.path

from fastapi import UploadFile, status, HTTPException

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

