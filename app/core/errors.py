class ServiceError(Exception):
    """应用异常，包含可安全展示给用户的提示和 HTTP 状态码。"""

    # 保存对外可展示的错误码、提示和 HTTP 状态码。
    def __init__(self, code: str, message: str, status_code: int):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class InputTooLong(ServiceError):
    # 构造输入超出上下文预算时的统一校验错误。
    def __init__(self):
        super().__init__("input_too_long", "Input exceeds the context budget.", 422)


class SessionBusy(ServiceError):
    # 构造同一会话已有请求运行时的冲突错误。
    def __init__(self):
        super().__init__("session_busy", "Session is processing another request.", 409)
