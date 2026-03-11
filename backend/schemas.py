from pydantic import BaseModel
from typing import Optional

class UserQuery(BaseModel):
    query: str
    user_id: Optional[str] = "demo_user"
    genre: Optional[str] = None
    min_rating: Optional[float] = 0.0
    media_type: Optional[str] = "All"     # "All", "movie", "tv"
    language_pref: Optional[str] = "all"  # "all", "en", "hi", "te"

class InteractionRequest(BaseModel):
    tmdb_id: int
    interaction_type: str  # "like", "dislike", "watchlist", "remove"

class WatchlistAction(BaseModel):
    tmdb_id: int
    action: str  # "add" or "remove"
