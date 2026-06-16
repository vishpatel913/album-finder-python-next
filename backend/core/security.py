"""Security primitives — token encode/verify, hashing.

One home for crypto, separate from the auth *flow* (``infrastructure/auth``) and
the request *guard* (``api/auth.py``). Wire to a JWT lib (e.g. PyJWT) when auth
lands.
"""


def create_access_token(subject: str, **claims: object) -> str:
    # TODO: jwt.encode({"sub": subject, **claims}, key, algorithm=...)
    raise NotImplementedError


def decode_access_token(token: str) -> dict:
    # TODO: jwt.decode(token, key, algorithms=[...])
    raise NotImplementedError
