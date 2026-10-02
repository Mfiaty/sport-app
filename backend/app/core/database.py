from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# Connexion à PostgreSQL
engine = create_engine(settings.database_url, pool_pre_ping=True)

# Fabrique de sessions : une session = un échange avec la base
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Classe mère de tous les modèles (tables)."""


def get_db():
    """Fournit une session aux routes, puis la ferme (injection de dépendances)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()