class InitError(Exception):
    def __init__(self, message):
        super().__init__(message)


class AddError(Exception):
    def __init__(self, message):
        super().__init__(message)


class RepoError(Exception):
    def __init__(self, message):
        super().__init__(message)


class DataError(Exception):
    def __init__(self, message):
        super().__init__(message)
