from .client import ScreenshotAPI
from .errors import (
    AuthenticationError,
    InsufficientCreditsError,
    InvalidAPIKeyError,
    NetworkError,
    ScreenshotAPIError,
    ScreenshotFailedError,
)
from .types import (
    ColorScheme,
    MockupDevice,
    ScreenshotFormat,
    ScreenshotMetadata,
    ScreenshotOptions,
    ScreenshotResult,
    WaitUntil,
)

__version__ = "1.0.0"

__all__ = [
    "__version__",
    "ScreenshotAPI",
    "ScreenshotAPIError",
    "AuthenticationError",
    "InsufficientCreditsError",
    "InvalidAPIKeyError",
    "ScreenshotFailedError",
    "NetworkError",
    "ScreenshotOptions",
    "ScreenshotMetadata",
    "ScreenshotResult",
    "ScreenshotFormat",
    "ColorScheme",
    "WaitUntil",
    "MockupDevice",
]
