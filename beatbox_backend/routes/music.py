import os
from sqlmodel import Session
from sqlalchemy import select
from beatbox_backend.models.music import Music as MusicModel
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from beatbox_backend.database import get_session
from typing import List
import shutil
from uuid import uuid4
import uuid
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
    music_id: uuid.UUID,
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
    title: str = Form(...),
    audio_file: UploadFile = File(...),
    image_file: UploadFile = File(...),
    session: Session = Depends(get_session)
) -> MusicModel:
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
        

    music = MusicModel(
        title=title,
        filename=unique_filename,
        img_path=image_filename
    )
    session.add(music)
    session.commit()
    session.refresh(music)
    return music

@router.delete("/{music_id}")
def delete_music(music_id: uuid.UUID, session: Session = Depends(get_session)):
    music = session.get(MusicModel, music_id)
    if not music:
        raise HTTPException(status_code=404, detail="Musique non trouvée")
    
    # Delete the music file from the server
    os.remove(os.path.join(UPLOAD_DIR, music.filename))
    os.remove(os.path.join(UPLOAD_DIR, music.img_path))

    session.delete(music)
    session.commit()
    return {"message": "Musique supprimée avec succès"}


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