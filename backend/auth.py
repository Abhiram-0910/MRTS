"""
auth.py — JWT Authentication + Authorization for Movie & TV Recommendation Engine.

Provides:
  - /token  POST endpoint (OAuth2PasswordRequestForm)
  - get_current_user()  FastAPI dependency (any logged-in user)
  - require_admin()     FastAPI dependency (admin-only)
  - create_access_token()  helper

Users are stored in the application database (the `users` table defined in
database.py), NOT in an in-memory dict.  The DB is seeded with an admin
account from env vars by database.init_db() so the system is ready immediately.
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from database import get_db, get_user_by_username

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────

# For production always set JWT_SECRET_KEY in .env.
# A random secret is generated per-process as a safe fallback (tokens issued by
# one process won't be valid after a restart — acceptable for dev, not prod).
SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

# ── Password Hashing ──────────────────────────────────────────────────────────

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── Database-Backed User Lookup ───────────────────────────────────────────────

def get_user(db: Session, username: str) -> Optional[dict]:
    """
    Fetch a user from the database by username.

    Returns a plain dict (for compatibility with the JWT dependency interface)
    or None if the user does not exist.
    """
    user_obj = get_user_by_username(db, username)
    return user_obj.to_dict() if user_obj else None


def authenticate_user(db: Session, username: str, password: str) -> Optional[dict]:
    """
    Verify credentials against the database.

    Returns the user dict on success, or None on any failure (unknown user,
    wrong password, or disabled account).
    """
    user = get_user(db, username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    if user.get("disabled"):
        return None
    return user


# ── Token Helpers ─────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ── FastAPI OAuth2 Scheme ─────────────────────────────────────────────────────

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> dict:
    """
    Dependency: decode the JWT bearer token and return the authenticated user dict.

    The database is consulted on every request so that account disablement
    takes effect immediately — it is NOT enough to just decode the JWT.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, role=payload.get("role"))
    except JWTError:
        raise credentials_exception

    user = get_user(db, token_data.username)
    if user is None or user.get("disabled"):
        raise credentials_exception
    return user


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency: requires admin role."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required.",
        )
    return current_user


# ── Router ────────────────────────────────────────────────────────────────────

router = APIRouter(tags=["auth"])


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    OAuth2 password flow. Returns a JWT bearer token.

    Credentials are validated against the `users` database table.
    The default admin account is seeded from ADMIN_USERNAME / ADMIN_PASSWORD
    env vars (defaults: admin / mirai2024) by database.init_db().
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=expire,
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
