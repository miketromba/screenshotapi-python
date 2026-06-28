from __future__ import annotations


class ScreenshotAPIError(Exception):
    def __init__(self, message: str, status: int, code: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code


class AuthenticationError(ScreenshotAPIError):
    def __init__(self, message: str) -> None:
        super().__init__(message, 401, "authentication_error")


class InsufficientCreditsError(ScreenshotAPIError):
    def __init__(self, message: str, balance: int) -> None:
        super().__init__(message, 402, "insufficient_credits")
        self.balance = balance


class InvalidAPIKeyError(ScreenshotAPIError):
    def __init__(self, message: str) -> None:
        super().__init__(message, 403, "invalid_api_key")


class ScreenshotFailedError(ScreenshotAPIError):
    def __init__(self, message: str) -> None:
        super().__init__(message, 500, "screenshot_failed")


class NetworkError(ScreenshotAPIError):
    def __init__(self, message: str) -> None:
        super().__init__(message, 0, "network_error")
