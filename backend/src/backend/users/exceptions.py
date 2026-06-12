class UserAlreadyExistsError(Exception):
    pass

class UserNotFoundError(Exception):
    pass

class PermissionDeniedError(Exception):
    pass