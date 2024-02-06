class CustomException(Exception):
    def __init__(self, code: int, message: str, log: str) -> None:
        self.code = code
        self.message = message
        self.log = log
        self.error = None


class UpscaleException(CustomException):
    def __init__(self, code: int, message: str, log: str, error=None) -> None:
        super().__init__(code, message, log)
        self.error = error
