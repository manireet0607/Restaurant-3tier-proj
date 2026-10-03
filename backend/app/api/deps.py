from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)
) -> User:
    unauthorized = HTTPException(
        status.HTTP_401_UNAUTHORIZED, "Not authenticated", headers={"WWW-Authenticate": "Bearer"}
    )
    if not creds:
        raise unauthorized
    payload = decode_access_token(creds.credentials)
    if not payload or not str(payload.get("sub", "")).isdigit():
        raise unauthorized
    user = db.get(User, int(payload["sub"]))
    if not user:
        raise unauthorized
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    # Role is read from the database, never trusted from the token alone.
    if user.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin access required")
    return user
