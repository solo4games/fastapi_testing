import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Documents(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(nullable=True)
    date: Mapped[datetime.datetime] = mapped_column(server_default=func.now())


class DocumentsText(Base):
    __tablename__ = "documents_text"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_doc: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    text: Mapped[str] = mapped_column(nullable=True)