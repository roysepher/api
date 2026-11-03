import hashlib
import secrets
from functools import lru_cache, wraps
from urllib.parse import urlsplit

import jwt
from flask import current_app, g, request
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from ..extensions import db
from ..models import User
from ..responses import error_response


@lru_cache(maxsize=4)
def _neon_jwks_client(jwks_url):
    return jwt.PyJWKClient(jwks_url)


def _decode_neon_token(token):
    base_url = current_app.config.get("NEON_AUTH_BASE_URL")
    jwks_url = current_app.config.get("NEON_AUTH_JWKS_URL")
    parsed_base_url = urlsplit(base_url or "")
    if not parsed_base_url.scheme or not parsed_base_url.netloc or not jwks_url:
        raise jwt.InvalidTokenError("Neon Auth is not configured")

    issuer = f"{parsed_base_url.scheme}://{parsed_base_url.netloc}"
    signing_key = _neon_jwks_client(jwks_url).get_signing_key_from_jwt(token).key
    return jwt.decode(
        token,
        signing_key,
        algorithms=["EdDSA"],
        issuer=issuer,
        audience=issuer,
        options={"require": ["exp", "sub", "iss", "aud"]},
    )


def _get_or_create_neon_user(subject):
    user = db.session.execute(
        db.select(User).filter_by(neon_auth_subject=subject)
    ).scalar_one_or_none()
    if user is not None:
        return user

    username_suffix = hashlib.sha256(subject.encode()).hexdigest()[:32]
    user = User(
        username=f"neon_{username_suffix}",
        password_hash=generate_password_hash(secrets.token_urlsafe(32)),
        neon_auth_subject=subject,
    )
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        user = db.session.execute(
            db.select(User).filter_by(neon_auth_subject=subject)
        ).scalar_one_or_none()
        if user is None:
            raise
    return user


def require_auth(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        authorization = request.headers.get("Authorization", "")
        scheme, separator, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not separator or not token.strip():
            return error_response(
                "invalid_token",
                "a Bearer token is required",
                401,
            )

        try:
            token = token.strip()
            algorithm = jwt.get_unverified_header(token).get("alg")
            if algorithm == "HS256":
                claims = jwt.decode(
                    token,
                    current_app.config["JWT_SECRET"],
                    algorithms=["HS256"],
                    options={"require": ["exp", "sub", "role"]},
                )
                g.user_id = int(claims["sub"])
                g.role = claims["role"]
                if not isinstance(g.role, str):
                    raise ValueError("role claim must be a string")
            elif algorithm == "EdDSA":
                claims = _decode_neon_token(token.strip())
                subject = claims.get("sub")
                if not isinstance(subject, str) or not subject or len(subject) > 255:
                    raise jwt.InvalidTokenError("invalid Neon Auth subject")
                user = _get_or_create_neon_user(subject)
                g.user_id = user.id
                g.role = user.role
            else:
                raise jwt.InvalidTokenError("unsupported token algorithm")
        except jwt.ExpiredSignatureError:
            return error_response(
                "invalid_token",
                "the token has expired",
                401,
            )
        except jwt.PyJWKClientConnectionError:
            current_app.logger.exception("Neon Auth JWKS endpoint is unavailable")
            return error_response(
                "auth_provider_unavailable",
                "authentication provider is unavailable",
                503,
            )
        except (jwt.InvalidTokenError, jwt.PyJWKClientError, KeyError, TypeError, ValueError):
            return error_response(
                "invalid_token",
                "the token is invalid",
                401,
            )

        return view(*args, **kwargs)

    return wrapped


def require_role(role):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if g.role != role:
                return error_response(
                    "forbidden",
                    f"{role} role is required",
                    403,
                )
            return view(*args, **kwargs)

        return wrapped

    return decorator
