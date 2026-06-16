"""Outbound port: identity / current caller.

Lets a use case ask "who is calling?" without knowing how auth works. The
adapter (token verification, user lookup) lives in ``infrastructure/auth`` and
is surfaced to routes via ``api/auth.py``.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class CurrentUser:
    id: str
    # TODO: add scopes/roles and a Spotify token reference as auth grows.


class IdentityPort(ABC):
    @abstractmethod
    def current_user(self, token: str) -> CurrentUser | None:
        """Resolve the user behind a credential, or None if invalid."""
        ...
