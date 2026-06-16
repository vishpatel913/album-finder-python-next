"""Request guard: extract the caller's identity for routes.

The thin FastAPI seam — reads the credential off the request and returns the
current user. Actual verification belongs to an ``IdentityPort`` adapter in
``infrastructure/auth``; this just wires it into ``Depends(...)``.

    @router.get("/me")
    def me(user: CurrentUser = Depends(get_current_user)): ...
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from application.ports.identity import CurrentUser

_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> CurrentUser:
    if creds is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    # TODO: resolve via an IdentityPort adapter (verify token -> user).
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Auth not implemented yet")
