from fastapi import HTTPException, status

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
