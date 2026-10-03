from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt

from app.core.config import get_settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode()[:72], bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode()[:72], password_hash.encode())
    except ValueError:
        return False


def create_access_token(user_id: int, role: str) -> str:
    s = get_settings()
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user_id), "role": role, "iat": now, "exp": now + timedelta(minutes=s.ACCESS_TOKEN_EXPIRE_MINUTES)}
    return jwt.encode(payload, s.SECRET_KEY, algorithm=s.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    s = get_settings()
    try:
        return jwt.decode(token, s.SECRET_KEY, algorithms=[s.JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None
