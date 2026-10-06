class ServiceError(Exception):
    """应用异常，包含可安全展示给用户的提示和 HTTP 状态码。"""

    def __init__(self, code: str, message: str, status_code: int):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class InputTooLong(ServiceError):
    def __init__(self):
        super().__init__("input_too_long", "Input exceeds the context budget.", 422)


class SessionBusy(ServiceError):
    def __init__(self):
        super().__init__("session_busy", "Session is processing another request.", 409)
