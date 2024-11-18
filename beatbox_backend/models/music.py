from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from fastapi import UploadFile, File

class Music(SQLModel, table=True):
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    title: str
    filename: str
    img_path: str