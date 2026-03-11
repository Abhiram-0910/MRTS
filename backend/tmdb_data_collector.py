import requests
import pandas as pd
import time
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    wait_fixed,
    before_sleep_log,
    RetryError,
)
import logging

logger = logging.getLogger(__name__)


class _RateLimitError(Exception):
    """
    Raised internally by ``_tmdb_get`` when TMDB returns HTTP 429.
    tenacity catches this class and applies the configured wait strategy.
    """
    def __init__(self, retry_after: float = 0.0):
        self.retry_after = retry_after
        super().__init__(f"TMDB rate-limited (Retry-After: {retry_after}s)")

class TMDBDataCollector:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/w500"

    # ── Core HTTP helper ─────────────────────────────────────────────────────

    @staticmethod
    def _retry_wait(retry_state) -> float:
        """
        Custom tenacity wait function.

        If the last exception was a ``_RateLimitError`` and TMDB supplied a
        ``Retry-After`` header, sleep for exactly that many seconds.
        Otherwise fall back to full-jitter exponential backoff (1-60 s).
        """
        exc = retry_state.outcome.exception()
        if isinstance(exc, _RateLimitError) and exc.retry_after > 0:
            print(f"[TMDB] Rate limited. Honouring Retry-After: {exc.retry_after}s")
            return exc.retry_after
        # Exponential backoff: 2^attempt seconds, capped at 60, with jitter
        exp = wait_exponential(multiplier=1, min=2, max=60)
        return exp(retry_state)

    def _tmdb_get(self, url: str, params: dict) -> requests.Response:
        """
        Central GET helper with tenacity-powered retry logic.

        Retry policy
        ------------
        * Catches only ``_RateLimitError`` (HTTP 429) and transient network
          errors (``requests.exceptions.RequestException``).
        * Up to 6 attempts total.
        * Wait time: ``Retry-After`` header value when present, else
          exponential backoff (2-60 s).
        * Raises ``RetryError`` after exhausting all attempts.
        """
        @retry(
            retry=retry_if_exception_type((_RateLimitError, requests.exceptions.RequestException)),
            stop=stop_after_attempt(6),
            wait=self._retry_wait,
            reraise=False,
            before_sleep=before_sleep_log(logger, logging.WARNING),
        )
        def _get() -> requests.Response:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 429:
                # Parse Retry-After if available (TMDB sends it as an integer)
                retry_after = float(resp.headers.get("Retry-After", 0))
                raise _RateLimitError(retry_after=retry_after)
            return resp

        return _get()

    def get_trending_movies(self, time_window: str = "week", page: int = 1) -> List[Dict]:
        """Get trending movies from TMDB."""
        url = f"{self.base_url}/trending/movie/{time_window}"
        params = {"api_key": self.api_key, "page": page}
        try:
            resp = self._tmdb_get(url, params)
            if resp.status_code == 200:
                return resp.json().get("results", [])
            print(f"Error fetching trending movies: {resp.status_code}")
        except Exception as exc:
            print(f"Exception in get_trending_movies: {exc}")
        return []

    def get_trending_tv_shows(self, time_window: str = "week", page: int = 1) -> List[Dict]:
        """Get trending TV shows from TMDB."""
        url = f"{self.base_url}/trending/tv/{time_window}"
        params = {"api_key": self.api_key, "page": page}
        try:
            resp = self._tmdb_get(url, params)
            if resp.status_code == 200:
                return resp.json().get("results", [])
            print(f"Error fetching trending TV shows: {resp.status_code}")
        except Exception as exc:
            print(f"Exception in get_trending_tv_shows: {exc}")
        return []

    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """Get detailed movie information."""
        url = f"{self.base_url}/movie/{movie_id}"
        params = {"api_key": self.api_key, "append_to_response": "credits,keywords,watch/providers"}
        try:
            resp = self._tmdb_get(url, params)
            if resp.status_code == 200:
                return resp.json()
            print(f"Error fetching movie details for {movie_id}: {resp.status_code}")
        except Exception as exc:
            print(f"Exception in get_movie_details({movie_id}): {exc}")
        return None

    def get_tv_show_details(self, tv_id: int) -> Optional[Dict]:
        """Get detailed TV show information."""
        url = f"{self.base_url}/tv/{tv_id}"
        params = {"api_key": self.api_key, "append_to_response": "credits,keywords,watch/providers"}
        try:
            resp = self._tmdb_get(url, params)
            if resp.status_code == 200:
                return resp.json()
            print(f"Error fetching TV show details for {tv_id}: {resp.status_code}")
        except Exception as exc:
            print(f"Exception in get_tv_show_details({tv_id}): {exc}")
        return None

    def discover_movies(self, page: int = 1, year_min: int = 2000, vote_min: float = 6.0) -> List[Dict]:
        """Discover movies based on criteria."""
        url = f"{self.base_url}/discover/movie"
        params = {
            "api_key": self.api_key,
            "page": page,
            "primary_release_date.gte": f"{year_min}-01-01",
            "vote_average.gte": vote_min,
            "sort_by": "popularity.desc",
            "with_original_language": "en,hi,te,ta,es,fr,de,it,ja,ko,zh",
        }
        try:
            resp = self._tmdb_get(url, params)
            if resp.status_code == 200:
                return resp.json().get("results", [])
            print(f"Error discovering movies: {resp.status_code}")
        except Exception as exc:
            print(f"Exception in discover_movies: {exc}")
        return []

    def discover_tv_shows(self, page: int = 1, year_min: int = 2000, vote_min: float = 6.0) -> List[Dict]:
        """Discover TV shows based on criteria."""
        url = f"{self.base_url}/discover/tv"
        params = {
            "api_key": self.api_key,
            "page": page,
            "first_air_date.gte": f"{year_min}-01-01",
            "vote_average.gte": vote_min,
            "sort_by": "popularity.desc",
            "with_original_language": "en,hi,te,ta,es,fr,de,it,ja,ko,zh",
        }
        try:
            resp = self._tmdb_get(url, params)
            if resp.status_code == 200:
                return resp.json().get("results", [])
            print(f"Error discovering TV shows: {resp.status_code}")
        except Exception as exc:
            print(f"Exception in discover_tv_shows: {exc}")
        return []

    def extract_genres(self, genres: List[Dict]) -> List[str]:
        """Extract genre names from genre objects"""
        return [genre["name"] for genre in genres if "name" in genre]
    
    def extract_cast(self, credits: Dict, limit: int = 5) -> List[str]:
        """Extract main cast members"""
        cast = credits.get("cast", [])[:limit]
        return [actor["name"] for actor in cast if "name" in actor]
    
    def extract_director(self, credits: Dict) -> Optional[str]:
        """Extract director name from credits"""
        crew = credits.get("crew", [])
        directors = [person["name"] for person in crew if person.get("job") == "Director"]
        return directors[0] if directors else None
    
    def extract_streaming_platforms(self, watch_providers: Dict, region: str = "US") -> List[str]:
        """Extract available streaming platforms"""
        platforms = []
        if "results" in watch_providers and region in watch_providers["results"]:
            region_data = watch_providers["results"][region]
            
            # Get flatrate (subscription) services
            if "flatrate" in region_data:
                platforms.extend([provider["provider_name"] for provider in region_data["flatrate"]])
            
            # Get free services
            if "free" in region_data:
                platforms.extend([provider["provider_name"] for provider in region_data["free"]])
            
            # Get rental services (if no subscription available)
            if not platforms and "rent" in region_data:
                platforms.extend([provider["provider_name"] for provider in region_data["rent"]])
        
        return list(set(platforms))  # Remove duplicates
    
    def process_movie_data(self, movie_data: Dict) -> Dict:
        """Process raw movie data into standardized format"""
        return {
            "id": movie_data.get("id"),
            "title": movie_data.get("title", ""),
            "overview": movie_data.get("overview", ""),
            "release_date": movie_data.get("release_date", ""),
            "rating": movie_data.get("vote_average", 0.0),
            "poster_path": movie_data.get("poster_path", ""),
            "media_type": "movie",
            "original_language": movie_data.get("original_language", "en"),
            "runtime": movie_data.get("runtime"),
            "budget": movie_data.get("budget"),
            "revenue": movie_data.get("revenue"),
            "status": movie_data.get("status", "released"),
            "tagline": movie_data.get("tagline", ""),
            "genres": self.extract_genres(movie_data.get("genres", [])),
            "cast": self.extract_cast(movie_data.get("credits", {})),
            "director": self.extract_director(movie_data.get("credits", {})),
            "streaming_platforms": self.extract_streaming_platforms(movie_data.get("watch/providers", {})),
            "popularity": movie_data.get("popularity", 0.0),
            "imdb_id": movie_data.get("imdb_id", ""),
            "keywords": [kw["name"] for kw in movie_data.get("keywords", {}).get("keywords", [])]
        }
    
    def process_tv_show_data(self, tv_data: Dict) -> Dict:
        """Process raw TV show data into standardized format"""
        return {
            "id": tv_data.get("id"),
            "title": tv_data.get("name", ""),
            "overview": tv_data.get("overview", ""),
            "release_date": tv_data.get("first_air_date", ""),
            "rating": tv_data.get("vote_average", 0.0),
            "poster_path": tv_data.get("poster_path", ""),
            "media_type": "tv",
            "original_language": tv_data.get("original_language", "en"),
            "runtime": tv_data.get("episode_run_time", [None])[0] if tv_data.get("episode_run_time") else None,
            "status": tv_data.get("status", "released"),
            "tagline": tv_data.get("tagline", ""),
            "genres": self.extract_genres(tv_data.get("genres", [])),
            "cast": self.extract_cast(tv_data.get("credits", {})),
            "director": self.extract_director(tv_data.get("credits", {})),
            "streaming_platforms": self.extract_streaming_platforms(tv_data.get("watch/providers", {})),
            "popularity": tv_data.get("popularity", 0.0),
            "number_of_seasons": tv_data.get("number_of_seasons"),
            "number_of_episodes": tv_data.get("number_of_episodes"),
            "keywords": [kw["name"] for kw in tv_data.get("keywords", {}).get("results", [])]
        }
    
    def collect_comprehensive_dataset(self, target_size: int = 10000, batch_size: int = 20) -> pd.DataFrame:
        """Collect comprehensive dataset with movies and TV shows."""
        all_media: list = []

        print(f"Starting comprehensive data collection targeting {target_size} titles...")

        # ── Trending content (high quality, recent) ───────────────────────────
        print("Collecting trending movies and TV shows...")
        trending_movies: list = []
        trending_tv: list = []

        for page in range(1, 6):  # 5 pages of trending content
            # No sleep needed — _tmdb_get retries with Retry-After when rate-limited
            trending_movies.extend(self.get_trending_movies("week", page))
            trending_tv.extend(self.get_trending_tv_shows("week", page))

        print(f"Found {len(trending_movies)} trending movies and {len(trending_tv)} trending TV shows")

        # ── Discovery content (diverse, high-rated) ───────────────────────────
        print("Discovering high-rated movies and TV shows...")
        discovered_movies: list = []
        discovered_tv: list = []

        for page in range(1, 21):  # 20 pages of discovered content
            discovered_movies.extend(self.discover_movies(page, year_min=2010, vote_min=7.0))
            discovered_tv.extend(self.discover_tv_shows(page, year_min=2010, vote_min=7.0))
            if page % 5 == 0:
                print(f"Completed {page} pages of discovery...")
            # No sleep here — tenacity handles rate limits inside each call

        print(f"Found {len(discovered_movies)} discovered movies and {len(discovered_tv)} discovered TV shows")

        # Combine and deduplicate by TMDB ID
        all_movie_ids = list(set(m["id"] for m in trending_movies + discovered_movies))
        all_tv_ids    = list(set(t["id"] for t in trending_tv    + discovered_tv))

        print(f"Processing {len(all_movie_ids)} unique movies and {len(all_tv_ids)} unique TV shows")

        # ── Process movies in parallel ────────────────────────────────────────
        print("Processing movie details...")
        with ThreadPoolExecutor(max_workers=5) as executor:
            movie_futures = [
                executor.submit(self.get_movie_details, mid)
                for mid in all_movie_ids[:5000]
            ]
            for future in as_completed(movie_futures):
                movie_data = future.result()
                if (
                    movie_data
                    and movie_data.get("overview")
                    and movie_data.get("vote_average", 0) > 5.0
                ):
                    all_media.append(self.process_movie_data(movie_data))
                # No time.sleep — rate-limit retries happen inside get_movie_details

        # ── Process TV shows in parallel ──────────────────────────────────────
        print("Processing TV show details...")
        with ThreadPoolExecutor(max_workers=5) as executor:
            tv_futures = [
                executor.submit(self.get_tv_show_details, tid)
                for tid in all_tv_ids[:5000]
            ]
            for future in as_completed(tv_futures):
                tv_data = future.result()
                if (
                    tv_data
                    and tv_data.get("overview")
                    and tv_data.get("vote_average", 0) > 5.0
                ):
                    all_media.append(self.process_tv_show_data(tv_data))
                # No time.sleep — rate-limit retries happen inside get_tv_show_details

        print(f"Successfully processed {len(all_media)} titles")

        # Convert to DataFrame
        df = pd.DataFrame(all_media)

        # Add additional metadata
        df["popularity_score"] = df["popularity"].fillna(0)
        df["trending_score"]   = 0.0
        df["last_updated"]     = datetime.utcnow()

        # Sort by popularity and rating
        df = df.sort_values(["popularity_score", "rating"], ascending=[False, False])

        # Limit to target size
        if len(df) > target_size:
            df = df.head(target_size)

        print(f"Final dataset contains {len(df)} titles")
        return df

    def save_dataset(self, df: pd.DataFrame, output_path: str = "../data/enhanced_dataset.csv"):
        """Save the collected dataset to CSV"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Dataset saved to {output_path}")
        
        # Also save separate files for movies and TV shows
        movies_df = df[df["media_type"] == "movie"]
        tv_df = df[df["media_type"] == "tv"]
        
        movies_df.to_csv("../data/enhanced_movies.csv", index=False)
        tv_df.to_csv("../data/enhanced_tv_shows.csv", index=False)
        
        print(f"Saved {len(movies_df)} movies and {len(tv_df)} TV shows separately")

def main():
    """Main function to collect comprehensive dataset"""
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        print("Please set TMDB_API_KEY environment variable")
        return
    
    collector = TMDBDataCollector(api_key)
    
    # Collect comprehensive dataset
    df = collector.collect_comprehensive_dataset(target_size=12000)
    
    # Save the dataset
    collector.save_dataset(df)
    
    # Print statistics
    print("\nDataset Statistics:")
    print(f"Total titles: {len(df)}")
    print(f"Movies: {len(df[df['media_type'] == 'movie'])}")
    print(f"TV Shows: {len(df[df['media_type'] == 'tv'])}")
    print(f"Average rating: {df['rating'].mean():.2f}")
    print(f"Languages: {df['original_language'].nunique()}")
    print(f"Streaming platforms found: {df['streaming_platforms'].apply(lambda x: len(x) if isinstance(x, list) else 0).sum()}")

if __name__ == "__main__":
    main()