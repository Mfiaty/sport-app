from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    # 12 caractères minimum, conformément aux recommandations de la CNIL
    password: str = Field(min_length=12, max_length=128)


class UserOut(BaseModel):
    """Ce que l'API renvoie d'un utilisateur : jamais le mot de passe haché."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"