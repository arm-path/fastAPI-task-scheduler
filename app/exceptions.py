from logging import exception

from fastapi import HTTPException, status

# Base
UnhandledException = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail={'code': 'fatal', 'msg': 'A server error occurred.'}
)

DatabaseQueryErrorException = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail={'code': 'fatal', 'msg': 'Database query error.'}
)

ForeignKeyDoesNotExistException = lambda msg: HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail={'code': 'exception', 'msg': msg}
)

NotUniqueValueException = lambda msg: HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail={'code': 'exception', 'msg': msg}
)

ForeignKeyDoesNotExistBaseException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail={'code': 'exception', 'msg': 'Violation of Foreign key field.'}
)

NotUniqueValueBaseException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail={'code': 'exception', 'msg': 'Violation of unique field.'}
)

ObjectNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail={'code': 'exception', 'msg': 'Object not found.'}
)

# Users

UserAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail={'code': 'exception', 'msg': 'User already exists.'}
)

UserOrPasswordEnteredIncorrectException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail={'code': 'exception', 'msg': 'The user or password entered is incorrect.'}
)

UserNotAuthorizedException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail={'code': 'exception', 'msg': 'User is not authorized.'}
)

URLTokenExpiredOrInvalidException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail={'code': 'exception', 'msg': 'URL Token is expired or invalid.'}
)

UserAlreadyActivatedException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail={'code': 'exception', 'msg': 'The user is already activated.'}
)

EmailAddressIsNotRegisteredException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail={'code': 'exception', 'msg': 'This email address is not registered.'}
)

PasswordsNotMatchException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail={'code': 'exception', 'msg': 'The passwords do not match.'}
)

# Categories

CategoryAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail={'code': 'exception', 'msg': 'A category with the same name already exists.'}
)

NotChangedCategoryDoesNotExistException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail={'code': 'exception', 'msg': 'Not changed, category does not exist.'}
)

FailedDeleteCategoryException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail={'code': 'exception', 'msg': 'Failed to delete category.'}
)

# Schedulers
ScheduleAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail={'code': 'exception', 'msg': 'A schedule with these days of the week already exists.'}
)

ScheduleNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail={'code': 'exception', 'msg': 'Schedule not found.'}
)

# Done Task

InvalidTaskIdException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail={'code': 'exception', 'msg': 'Invalid task_id.'}
)

NotAccordingToScheduleException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail={'code': 'exception', 'msg': 'Not according to schedule.'}
)

QuantityCannotNegativeException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail={'code': 'exception', 'msg': 'Quantity cannot be negative.'}
)

DoneTaskAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail={'code': 'exception', 'msg': 'The task already exists.'}
)

DatesIncorrectException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail={'code': 'exception', 'msg': 'The dates are incorrect.'}
)

NotTasksFoundByDateException = lambda date_start, date_end: HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail={'code': 'info', 'msg': f'No tasks found by date: {date_start} to {date_end}'}
)

# Reports
ParamDatesMustBeDefinedException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail={'code': 'exception', 'msg': 'date_from and date_to must be defined'}
)

