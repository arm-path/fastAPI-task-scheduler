from asyncpg import ForeignKeyViolationError, UniqueViolationError

from app.exceptions import (ForeignKeyDoesNotExistException,
                            UnhandledException,
                            NotUniqueValueException,
                            ForeignKeyDoesNotExistBaseException,
                            NotUniqueValueBaseException)


class ExceptionsDatabase:
    def __init__(self,
                 unique_error=None,
                 fk_error=None,
                 object_not_found = None,
                 detail=False,
                 ):
        self.unique_error = unique_error
        self.fk_error = fk_error
        self.detail = detail
        self.no_object_found_to_update = object_not_found


def integrity_error_handling(err, exceptions: ExceptionsDatabase):
    if err.orig.__cause__.__class__ == UniqueViolationError:
        if exceptions.unique_error:
            raise exceptions.unique_error
        elif exceptions.detail:
            raise NotUniqueValueException(unique_violation_error(err))
        else:
            raise NotUniqueValueBaseException
    elif err.orig.__cause__.__class__ == ForeignKeyViolationError:
        if exceptions.fk_error:
            raise exceptions.fk_error
        elif exceptions.detail:
            raise ForeignKeyDoesNotExistException(fk_violation_error(err))
        else:
            raise ForeignKeyDoesNotExistBaseException
    else:

        raise UnhandledException


def unique_violation_error(err):
    detail_index = str(err.orig).find("DETAIL:") + 7
    if detail_index != -1:
        detail_text = str(err.orig)[detail_index:].strip()
        return detail_text
    return 'Unique field error'


def fk_violation_error(err):
    detail_index = str(err.orig).find("DETAIL:") + 7
    if detail_index != -1:
        detail_text = str(err.orig)[detail_index:].strip()
        return detail_text
    return 'Foreign key error'
