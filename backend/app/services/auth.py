from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import DUMMY_HASH, hash_password, verify_password
from app.models import User
from app.repositories import users as users_repo


class EmailAlreadyUsedError(Exception):
    """L'adresse e-mail est déjà associée à un compte."""


def _normalize(email: str) -> str:
    return email.strip().lower()


def register(db: Session, email: str, password: str) -> User:
    email = _normalize(email)
    if users_repo.get_by_email(db, email) is not None:
        raise EmailAlreadyUsedError
    try:
        return users_repo.create(db, email, hash_password(password))
    except IntegrityError:
        # Deux inscriptions simultanées avec le même e-mail
        db.rollback()
        raise EmailAlreadyUsedError from None


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = users_repo.get_by_email(db, _normalize(email))
    if user is None:
        # Même temps de calcul que pour un vrai compte
        verify_password(password, DUMMY_HASH)
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user