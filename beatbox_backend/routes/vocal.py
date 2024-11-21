import os
from sqlmodel import Session
from sqlalchemy import select
from beatbox_backend.models.music import Vocal as VocalModel
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from beatbox_backend.database import get_session
from typing import List
import shutil
from uuid import uuid4
import uuid
router = APIRouter(
    prefix="/vocal",
    tags=["Vocal"],
)


UPLOAD_DIR = "music/vocals"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/")
def get_vocals(session: Session = Depends(get_session)) -> List[VocalModel]:
    statement = select(VocalModel)
    result = session.exec(statement)
    vocals = result.scalars().all()
    return list(vocals)


@router.get("/{vocal_id}")
def get_vocal(vocal_id: uuid.UUID, session: Session = Depends(get_session)) -> VocalModel:
    vocal = session.get(VocalModel, vocal_id)
    if not vocal:
        raise HTTPException(status_code=404, detail="Vocal non trouvé")
    return vocal


@router.get("/beat/{beat_id}")
def get_vocals_by_beat_id(beat_id: uuid.UUID, session: Session = Depends(get_session)) -> List[VocalModel]:
    statement = select(VocalModel).where(VocalModel.beat_id == beat_id)
    result = session.exec(statement)
    vocals = result.scalars().all()
    return list(vocals)


@router.get("/download/{vocal_id}")
def get_vocal_file(
    vocal_id: uuid.UUID,
    session: Session = Depends(get_session)
) -> FileResponse:
    # Récupère la musique par son ID
    vocal = session.get(VocalModel, vocal_id)
    if not vocal:
        raise HTTPException(status_code=404, detail="vocal non trouvé")

    # Construit le chemin complet du fichier
    file_path = os.path.join(UPLOAD_DIR, vocal.filename)
    
    # Vérifie si le fichier existe
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="Fichier audio non trouvé sur le serveur"
        )

    return FileResponse(
        file_path,
        media_type="audio/wav",
        filename=vocal.filename
    )


@router.post("/")
async def post_vocal(
    title: str = Form(...),
    artist: str = Form(...),
    beat_id: uuid.UUID = Form(...),
    audio_file: UploadFile = File(...),
    session: Session = Depends(get_session)
) -> VocalModel:
    if not audio_file.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="Le fichier doit être un fichier audio")

    # Traitement du fichier audio
    file_extension = os.path.splitext(audio_file.filename)[-1]
    filename = audio_file.filename.split(".")[0]
    unique_filename = f"{filename}-{uuid4().hex}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'enregistrement du fichier audio : {str(e)}")       

    vocal = VocalModel(
        title=title,
        artist=artist,
        beat_id=beat_id,
        filename=unique_filename,
    )
    session.add(vocal)
    session.commit()
    session.refresh(vocal)
    return vocal

@router.delete("/{vocal_id}")
def delete_vocal(vocal_id: uuid.UUID, session: Session = Depends(get_session)):
    vocal = session.get(VocalModel, vocal_id)
    if not vocal:
        raise HTTPException(status_code=404, detail="vocal non trouvé")
    
    # Delete the music file from the server
    try:    
        os.remove(os.path.join(UPLOAD_DIR, vocal.filename))
    except Exception as e:
        print(e)

    session.delete(vocal)
    session.commit()
    return {"message": "vocal supprimé avec succès"}
