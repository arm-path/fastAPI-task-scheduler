from asyncpg import ForeignKeyViolationError

from app.exceptions import ForeignKeyDoesNotExistException, UnhandledException


def integrity_error_handling(err):
    if err.orig.__cause__.__class__ == ForeignKeyViolationError:
        detail_index = str(err.orig).find("DETAIL:") + 7
        if detail_index != -1:
            detail_text = str(err.orig)[detail_index:].strip()
            raise ForeignKeyDoesNotExistException(detail_text)
        raise UnhandledException
    raise UnhandledException