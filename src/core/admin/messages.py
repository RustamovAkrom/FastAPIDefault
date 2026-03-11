from fastapi import Request


def pop_admin_error(request: Request) -> str | None:
    error = request.session.pop("_admin_error", None)

    if isinstance(error, str):
        return error

    return None
