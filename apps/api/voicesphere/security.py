from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings
from .db import get_db
from .models import Membership, User

password_hash = PasswordHash.recommended()
oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def create_token(user: User, membership: Membership) -> str:
    expiry = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_minutes
    )
    return jwt.encode(
        {"sub": str(user.id), "org": membership.organization_id, "exp": expiry},
        settings.app_secret_key,
        algorithm="HS256",
    )


def current_identity(token: str = Depends(oauth2), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.app_secret_key, algorithms=["HS256"])
        uid, oid = int(payload["sub"]), int(payload["org"])
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.get(User, uid)
    membership = (
        db.query(Membership).filter_by(user_id=uid, organization_id=oid).first()
    )
    if not user or not user.active or not membership:
        raise HTTPException(
            status_code=401, detail="User is not an active organization member"
        )
    return user, membership


def require_roles(*roles):
    def check(identity=Depends(current_identity)):
        user, membership = identity
        if membership.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return identity

    return check
