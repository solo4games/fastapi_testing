from fastapi import FastAPI

from app.documents.router import router as documents_router

app = FastAPI()

app.include_router(documents_router)