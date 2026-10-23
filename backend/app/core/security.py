# Security / OIDC Configuration
from typing import Optional
from pydantic import BaseModel
from jose import jwt, JWTError
import httpx

from backend.app.core.config import get_settings


class TokenData(BaseModel):
    sub: str
    email: Optional[str] = None
    roles: list[str] = []
    exp: Optional[int] = None


class OIDCConfig(BaseModel):
    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    jwks_uri: str
    userinfo_endpoint: str
    end_session_endpoint: str


_settings = None


def get_oidc_config() -> OIDCConfig:
    """Fetch OIDC configuration from Keycloak discovery endpoint."""
    global _settings
    if _settings is None:
        _settings = get_settings()
    settings = _settings

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(f"{settings.OIDC_ISSUER_URL}/.well-known/openid-configuration")
            resp.raise_for_status()
            data = resp.json()
            return OIDCConfig(**data)
    except Exception:
        # Return default config for demo mode
        return OIDCConfig(
            issuer=settings.OIDC_ISSUER_URL,
            authorization_endpoint=f"{settings.OIDC_ISSUER_URL}/protocol/openid-connect/auth",
            token_endpoint=f"{settings.OIDC_ISSUER_URL}/protocol/openid-connect/token",
            jwks_uri=f"{settings.OIDC_ISSUER_URL}/protocol/openid-connect/certs",
            userinfo_endpoint=f"{settings.OIDC_ISSUER_URL}/protocol/openid-connect/userinfo",
            end_session_endpoint=f"{settings.OIDC_ISSUER_URL}/protocol/openid-connect/logout",
        )


def get_jwks() -> dict:
    """Fetch JWKS from Keycloak."""
    settings = get_settings()
    oidc_config = get_oidc_config()
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(oidc_config.jwks_uri)
            resp.raise_for_status()
            return resp.json()
    except Exception:
        return {"keys": []}


def validate_token(token: str) -> TokenData:
    """Validate JWT token using Keycloak JWKS."""
    settings = get_settings()

    if settings.DEMO_MODE:
        # Demo mode: accept any token with valid structure
        try:
            payload = jwt.decode(token, key="", options={"verify_signature": False})
            return TokenData(
                sub=payload.get("sub", "demo-user"),
                email=payload.get("email"),
                roles=payload.get("realm_access", {}).get("roles", []),
                exp=payload.get("exp"),
            )
        except JWTError:
            pass

    # Production mode: validate with JWKS
    jwks = get_jwks()
    try:
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=settings.OIDC_AUDIENCE,
            issuer=settings.OIDC_ISSUER_URL,
        )
        return TokenData(
            sub=payload.get("sub", ""),
            email=payload.get("email"),
            roles=payload.get("realm_access", {}).get("roles", []),
            exp=payload.get("exp"),
        )
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}")


def require_role(token_data: TokenData, required_roles: list[str]) -> bool:
    """Check if token has required role."""
    return any(role in token_data.roles for role in required_roles)