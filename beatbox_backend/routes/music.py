import os
from sqlmodel import Session
from sqlalchemy import select
from beatbox_backend.models.music import Music as MusicModel
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from beatbox_backend.database import get_session
from typing import List
import shutil
from uuid import uuid4

router = APIRouter(
    prefix="/music",
    tags=["Music"],
)


UPLOAD_DIR = "music/prods"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/")
def get_musics(session: Session = Depends(get_session)) -> List[MusicModel]:
    statement = select(MusicModel)
    result = session.exec(statement)
    musics = result.scalars().all()
    return list(musics)

@router.get("/{music_id}")
def get_music_file(
    music_id: int,
    session: Session = Depends(get_session)
) -> FileResponse:
    # Récupère la musique par son ID
    music = session.get(MusicModel, music_id)
    if not music:
        raise HTTPException(status_code=404, detail="Musique non trouvée")

    # Construit le chemin complet du fichier
    file_path = os.path.join(UPLOAD_DIR, music.filename)
    
    # Vérifie si le fichier existe
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="Fichier audio non trouvé sur le serveur"
        )

    return FileResponse(
        file_path,
        media_type="audio/wav",
        filename=music.filename
    )

@router.post("/")
async def post_music(
    title: str,
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
) -> MusicModel:
    if not file.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="Le fichier doit être un fichier audio")

    file_extension = os.path.splitext(file.filename)[-1]
    filename = file.filename.split(".")[0]
    unique_filename = f"{filename}-{uuid4().hex}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'enregistrement du fichier : {str(e)}")

    music = MusicModel(title=title, filename=unique_filename)
    session.add(music)
    session.commit()
    session.refresh(music)
    return music