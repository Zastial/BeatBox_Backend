import os
from sqlmodel import Session
from sqlalchemy import select
from beatbox_backend.models.music import Beat as BeatModel
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from beatbox_backend.models.music import Vocal as VocalModel
from beatbox_backend.database import get_session
from typing import List
import shutil
from uuid import uuid4
import uuid
router = APIRouter(
    prefix="/beat",
    tags=["Beat"],
)


UPLOAD_DIR = "music/beats"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/")
def get_beats(session: Session = Depends(get_session)) -> List[BeatModel]:
    statement = select(BeatModel)
    result = session.exec(statement)
    beats = result.scalars().all()
    return list(beats)


@router.get("/{beat_id}")
def get_beat(beat_id: uuid.UUID, session: Session = Depends(get_session)) -> BeatModel:
    beat = session.get(BeatModel, beat_id)
    if not beat:
        raise HTTPException(status_code=404, detail="Beat non trouvé")
    return beat


@router.get("/download/{beat_id}")
def get_beat_file(
    beat_id: uuid.UUID,
    session: Session = Depends(get_session)
) -> FileResponse:
    # Récupère la musique par son ID
    beat = session.get(BeatModel, beat_id)
    if not beat:
        raise HTTPException(status_code=404, detail="Beat non trouvé")

    # Construit le chemin complet du fichier
    file_path = os.path.join(UPLOAD_DIR, beat.filename)
    
    # Vérifie si le fichier existe
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="Fichier audio non trouvé sur le serveur"
        )

    return FileResponse(
        file_path,
        media_type="audio/wav",
        filename=beat.filename
    )


@router.post("/")
async def post_beat(
    title: str = Form(...),
    artist: str = Form(...),
    audio_file: UploadFile = File(...),
    image_file: UploadFile = File(...),
    session: Session = Depends(get_session)
) -> BeatModel:
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

    if not image_file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Le fichier doit être une image")
        
    img_extension = os.path.splitext(image_file.filename)[-1]
    img_filename = image_file.filename.split(".")[0]
    unique_img_filename = f"{img_filename}-{uuid4().hex}{img_extension}"
    img_path = os.path.join(UPLOAD_DIR, unique_img_filename)

    try:
        with open(img_path, "wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)
        image_filename = unique_img_filename
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'enregistrement de l'image : {str(e)}")
        

    beat = BeatModel(
        title=title,
        artist=artist,
        filename=unique_filename,
        img_path=image_filename
    )
    session.add(beat)
    session.commit()
    session.refresh(beat)
    return beat

@router.delete("/{beat_id}")
def delete_beat(beat_id: uuid.UUID, session: Session = Depends(get_session)):
    beat = session.get(BeatModel, beat_id)
    if not beat:
        raise HTTPException(status_code=404, detail="Beat non trouvé")
    
    vocals = session.exec(select(VocalModel).where(VocalModel.beat_id == beat_id)).scalars().all()
    for vocal in vocals:
        session.delete(vocal)
    
    try:
        os.remove(os.path.join(UPLOAD_DIR, beat.filename))
        os.remove(os.path.join(UPLOAD_DIR, beat.img_path))
    except Exception as e:
        print(e)

    session.delete(beat)
    session.commit()
    return {"message": "Beat supprimé avec succès"}


@router.get("/image/{image_filename}")
def get_image_file(image_filename: str) -> FileResponse:
    # Construit le chemin complet du fichier
    file_path = os.path.join(UPLOAD_DIR, image_filename)
    
    # Vérifie si le fichier existe
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="Image non trouvée sur le serveur"
        )

    # Détermine le type MIME en fonction de l'extension
    extension = os.path.splitext(image_filename)[1].lower()
    content_type = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }.get(extension, 'application/octet-stream')

    return FileResponse(
        file_path,
        media_type=content_type,
        filename=image_filename
    )