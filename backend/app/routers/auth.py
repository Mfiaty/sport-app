from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import create_access_token
from app.models import User
from app.schemas.auth import Token, UserCreate, UserOut
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """Crée un compte."""
    try:
        return auth_service.register(db, data.email, data.password)
    except auth_service.EmailAlreadyUsedError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Cet e-mail est déjà utilisé") from None


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Connexion : le champ « username » contient l'adresse e-mail."""
    user = auth_service.authenticate(db, form.username, form.password)
    if user is None:
        # Message volontairement vague : on ne dit pas si c'est l'e-mail ou le mot de passe
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(str(user.id)))


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    """Le compte actuellement connecté."""
    return current_user