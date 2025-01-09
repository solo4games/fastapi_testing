from fastapi import FastAPI, Depends, APIRouter
from typing import Optional
from fastapi import Query
from pydantic import BaseModel

from app.documents.router import router as documents_router

app = FastAPI()

app.include_router(documents_router)