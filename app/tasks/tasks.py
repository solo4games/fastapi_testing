import os.path
from PIL import Image

import pytesseract
from fastapi import HTTPException

from app.tasks.celery import celery_app


@celery_app.task(name='app.tasks.tasks.analyze_document_task')
def analyze_document_task(path: str) -> str:
    if os.path.isfile(path):
        return pytesseract.image_to_string(Image.open(path))
    raise HTTPException(status_code=404, detail="Document image not found")
