import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings

# Paramètres scrypt : coût élevé en calcul ET en mémoire,
# ce qui rend les attaques par force brute très lentes
_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1
_KEY_LENGTH = 64


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii")


def _b64decode(text: str) -> bytes:
    return base64.urlsafe_b64decode(text.encode("ascii"))


def hash_password(password: str) -> str:
    """Hache un mot de passe avec un sel aléatoire unique."""
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
        dklen=_KEY_LENGTH,
    )
    # Format stocké : algorithme$n$r$p$sel$empreinte
    return "$".join(
        ["scrypt", str(_SCRYPT_N), str(_SCRYPT_R), str(_SCRYPT_P), _b64encode(salt), _b64encode(digest)]
    )


def verify_password(password: str, stored_hash: str) -> bool:
    """Vérifie un mot de passe, en temps constant."""
    try:
        algorithm, n, r, p, salt_b64, hash_b64 = stored_hash.split("$")
    except ValueError:
        return False
    if algorithm != "scrypt":
        return False

    expected = _b64decode(hash_b64)
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=_b64decode(salt_b64),
        n=int(n),
        r=int(r),
        p=int(p),
        dklen=len(expected),
    )
    # compare_digest évite de deviner l'empreinte en mesurant le temps de réponse
    return hmac.compare_digest(digest, expected)


# Empreinte factice : utilisée quand l'e-mail n'existe pas, pour que la réponse
# prenne le même temps et ne révèle pas quels comptes existent
DUMMY_HASH = hash_password(secrets.token_urlsafe(16))


def create_access_token(subject: str) -> str:
    """Crée un jeton signé, valable un temps limité."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str | None:
    """Renvoie l'identifiant contenu dans le jeton, ou None s'il est invalide ou expiré."""
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
    except jwt.InvalidTokenError:
        return None
    return payload.get("sub")