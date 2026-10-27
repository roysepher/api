from functools import wraps

import jwt
from flask import current_app, g, request

from ..responses import error_response


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
            claims = jwt.decode(
                token.strip(),
                current_app.config["JWT_SECRET"],
                algorithms=["HS256"],
                options={"require": ["exp", "sub", "role"]},
            )
            g.user_id = int(claims["sub"])
            g.role = claims["role"]
            if not isinstance(g.role, str):
                raise ValueError("role claim must be a string")
        except jwt.ExpiredSignatureError:
            return error_response(
                "invalid_token",
                "the token has expired",
                401,
            )
        except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
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
