from sqlmodel import Session
from sqlalchemy import select
from beatbox_backend.models.Users import Users
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from beatbox_backend.database import get_session
from typing import List
from beatbox_backend.models.Music import Music, Beat, Vocal
from passlib.context import CryptContext

# Configuration du contexte de hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


def verify_password(plain_password, hashed_password):
    """Vérifie si le mot de passe en clair correspond au mot de passe haché"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Génère un hash à partir du mot de passe en clair"""
    return pwd_context.hash(password)


@router.get("/")
def get_users(session: Session = Depends(get_session)) -> List[Users]:
    statement = select(Users)
    result = session.exec(statement)
    users = result.scalars().all()
    return list(users)


@router.post("/signup")
def create_user(name: str = Form(...), email: str = Form(...), password: str = Form(...), session: Session = Depends(get_session)):
    # Vérifier si l'utilisateur existe déjà
    statement = select(Users).where(Users.email == email)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Créer un nouvel utilisateur avec le mot de passe haché
    hashed_password = get_password_hash(password)
    user = Users(name=name, email=email, password=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Retourner l'utilisateur sans le mot de passe
    user_data = user.dict()
    user_data.pop("password", None)
    return user_data


@router.post("/login")
def login_user(email: str = Form(...), password: str = Form(...), session: Session = Depends(get_session)):
    statement = select(Users).where(Users.email == email)
    result = session.exec(statement)
    user = result.scalars().first()
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Vérifier le mot de passe haché
    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Retourner l'utilisateur sans le mot de passe
    user_data = user.dict()
    user_data.pop("password", None)
    return user_data