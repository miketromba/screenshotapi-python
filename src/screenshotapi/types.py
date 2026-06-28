from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional, Sequence

ScreenshotFormat = Literal["png", "jpeg", "webp", "pdf"]
ColorScheme = Literal["light", "dark"]
WaitUntil = Literal["load", "domcontentloaded", "networkidle0", "networkidle2"]
MockupDevice = Literal["browser", "iphone", "macbook"]

@dataclass
class ScreenshotOptions:
    url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    full_page: Optional[bool] = None
    type: Optional[ScreenshotFormat] = None
    quality: Optional[int] = None
    color_scheme: Optional[ColorScheme] = None
    wait_until: Optional[WaitUntil] = None
    wait_for_selector: Optional[str] = None
    delay: Optional[int] = None
    block_ads: Optional[bool] = None
    remove_cookie_banners: Optional[bool] = None
    html: Optional[str] = None
    css_inject: Optional[str] = None
    js_inject: Optional[str] = None
    stealth_mode: Optional[bool] = None
    device_pixel_ratio: Optional[int] = None
    timezone: Optional[str] = None
    locale: Optional[str] = None
    cache_ttl: Optional[int] = None
    preload_fonts: Optional[bool] = None
    remove_elements: Optional[Sequence[str]] = None
    remove_popups: Optional[bool] = None
    mockup_device: Optional[MockupDevice] = None
    geo_latitude: Optional[float] = None
    geo_longitude: Optional[float] = None
    geo_accuracy: Optional[float] = None


@dataclass
class ScreenshotMetadata:
    credits_remaining: int
    screenshot_id: str
    duration_ms: int


@dataclass
class ScreenshotResult:
    image: bytes
    metadata: ScreenshotMetadata
    content_type: str
