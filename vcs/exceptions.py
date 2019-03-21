class CustomException(Exception):
    pass


class InitError(CustomException):
    def __init__(self, message):
        super().__init__(message)


class AddError(CustomException):
    def __init__(self, message):
        super().__init__(message)


class RepoError(CustomException):
    def __init__(self, message):
        super().__init__(message)


class DataError(CustomException):
    def __init__(self, message):
        super().__init__(message)
