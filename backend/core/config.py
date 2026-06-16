"""Application settings — cross-cutting config, read from the environment.

Dependency-free for now; swap for ``pydantic-settings`` (BaseSettings) when you
want typed parsing/validation.
"""

import os


class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@database:5432/music_library"
    )
    spotify_client_id: str | None = os.getenv("SPOTIPY_CLIENT_ID")
    spotify_client_secret: str | None = os.getenv("SPOTIPY_CLIENT_SECRET")
    spotify_redirect_uri: str | None = os.getenv("SPOTIFY_REDIRECT_URI")


settings = Settings()
