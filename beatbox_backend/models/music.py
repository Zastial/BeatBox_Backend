from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from sqlmodel import Relationship

class Vocal(SQLModel, table=True):
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    title: str
    filename: str
    artist: str
    beat_id: UUID = Field(foreign_key="beat.id")
    beat: "Beat" = Relationship(back_populates="vocals")
    user_id: UUID | None = Field(foreign_key="users.id", nullable=True)
    user: "Users" = Relationship(back_populates="vocals")


class Beat(SQLModel, table=True):
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    title: str
    filename: str
    img_path: str
    artist: str
    vocals: list["Vocal"] = Relationship(back_populates="beat")
    user_id: UUID | None = Field(foreign_key="users.id", nullable=True)
    user: "Users" = Relationship(back_populates="beats")


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
    artist: str
    vocal_id: UUID | None = Field(foreign_key="vocal.id")
    beat_id: UUID | None = Field(foreign_key="beat.id")
    vocal: "Vocal" = Relationship()
    beat: "Beat" = Relationship()
    user_id: UUID | None = Field(foreign_key="users.id", nullable=True)
    user: "Users" = Relationship(back_populates="musics")