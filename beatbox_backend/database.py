from typing import Generator
from sqlmodel import create_engine, Session
from beatbox_backend.settings import settings
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlmodel import SQLModel

engine = create_engine(settings.postgres_dsn)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Initialisation de la base de données avant le démarrage du serveur
    SQLModel.metadata.create_all(engine)
