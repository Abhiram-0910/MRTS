from sqlalchemy import create_engine, Column, Integer, String, Float, Text, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional

load_dotenv()

# We try to connect to PostgreSQL as requested. 
# If credentials fail, the user can easily switch to SQLite locally by modifying DATABASE_URL.
# Defaulting to an SQLite fallback so the project runs immediately without requiring a running Postgres server.
try:
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./mirai.db")
    
    # SQLite requires check_same_thread=False for FastAPI concurrency
    if DATABASE_URL.startswith("sqlite"):
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(DATABASE_URL)
except Exception as e:
    DATABASE_URL = "sqlite:///./mirai.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Media(Base):
    __tablename__ = "media"

    db_id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, index=True)
    title = Column(String, index=True)
    overview = Column(Text)
    release_date = Column(String)
    rating = Column(Float)
    poster_path = Column(String)
    media_type = Column(String, default="movie", index=True) # "movie" or "tv"

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True) # Simple string ID for local use
    tmdb_id = Column(Integer, index=True)
    interaction_type = Column(String) # "like", "dislike"
    timestamp = Column(DateTime, default=datetime.utcnow)


class User(Base):
    """
    Application user account stored in the database.

    Replaces the previous in-memory USERS_DB dict in auth.py so that users
    persist across restarts and can be managed at runtime (create, disable, etc.).
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False)  # "admin" | "user"
    disabled = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        """Serialize to a plain dict compatible with the auth dependency interface."""
        return {
            "id": self.id,
            "username": self.username,
            "hashed_password": self.hashed_password,
            "role": self.role,
            "disabled": self.disabled,
        }

# ── Query helpers ─────────────────────────────────────────────────────────────

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Return the User ORM object, or None if not found."""
    return db.query(User).filter(User.username == username).first()


# ── DB initialisation + admin seeding ─────────────────────────────────────────

def init_db():
    """
    Create all tables and, if the `users` table is empty, seed the admin
    account from ADMIN_USERNAME / ADMIN_PASSWORD env vars.

    This is intentionally idempotent: safe to call on every startup.
    """
    Base.metadata.create_all(bind=engine)
    _seed_admin()


def _seed_admin():
    """
    Insert the default admin user the first time the DB is initialised.
    Uses passlib to hash the password the same way auth.py does — we import
    lazily to avoid a circular dependency.
    """
    from passlib.context import CryptContext  # local import avoids circular dep

    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "mirai2024")

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == admin_username).first()
        if existing:
            return  # already seeded; nothing to do

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        admin = User(
            username=admin_username,
            hashed_password=pwd_context.hash(admin_password),
            role="admin",
            disabled=False,
        )
        db.add(admin)
        db.commit()
        print(f"[database] Seeded admin user '{admin_username}'.")
    except Exception as e:
        db.rollback()
        print(f"[database] Admin seeding failed: {e}")
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
