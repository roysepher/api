from sqlalchemy.exc import IntegrityError


def is_username_unique_violation(error: IntegrityError) -> bool:
    original = error.orig
    if (
        getattr(original, "sqlite_errorname", None) == "SQLITE_CONSTRAINT_UNIQUE"
        and str(original) == "UNIQUE constraint failed: user.username"
    ):
        return True

    return (
        getattr(original, "sqlstate", None) == "23505"
        and getattr(getattr(original, "diag", None), "constraint_name", None)
        == "user_username_key"
    )
