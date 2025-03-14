from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from sqlmodel import Relationship

class Users(SQLModel, table=True):
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    name: str
    email: str
    password: str
    musics: list["Music"] = Relationship(back_populates="user")
    beats: list["Beat"] = Relationship(back_populates="user")
    vocals: list["Vocal"] = Relationship(back_populates="user")