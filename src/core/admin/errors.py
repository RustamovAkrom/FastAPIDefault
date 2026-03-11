from sqladmin.exceptions import SQLAdminException


def admin_error(message: str) -> None:
    raise SQLAdminException(message)
