"""Spotify OAuth — the auth *flow* (token exchange & refresh), not the guard.

Talks to Spotify's auth endpoints and persists/refreshes user tokens. The
request-time guard that injects the current user lives in ``api/auth.py``;
crypto primitives live in ``core/security.py``.
"""


class SpotifyOAuth:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri

    def authorize_url(self, state: str) -> str:
        # TODO: build the Spotify consent URL.
        raise NotImplementedError

    def exchange_code(self, code: str) -> dict:
        # TODO: exchange an auth code for access/refresh tokens.
        raise NotImplementedError

    def refresh(self, refresh_token: str) -> dict:
        # TODO: refresh an access token.
        raise NotImplementedError
