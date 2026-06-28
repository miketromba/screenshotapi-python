from __future__ import annotations

from collections.abc import Mapping as MappingABC
from collections.abc import Sequence as SequenceABC
from pathlib import Path
from typing import Dict, Mapping, NoReturn, Optional, Sequence, Union

import httpx

from .errors import (
    AuthenticationError,
    InsufficientCreditsError,
    InvalidAPIKeyError,
    NetworkError,
    ScreenshotAPIError,
    ScreenshotFailedError,
)
from .types import ScreenshotMetadata, ScreenshotOptions, ScreenshotResult

DEFAULT_BASE_URL = "https://screenshotapi.to"
DEFAULT_TIMEOUT = 60.0

ScreenshotOptionsInput = Union[ScreenshotOptions, Mapping[str, object]]


class ScreenshotAPI:
    """Client for the ScreenshotAPI service."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        transport: Optional[httpx.BaseTransport] = None,
        async_transport: Optional[httpx.AsyncBaseTransport] = None,
    ) -> None:
        if not api_key:
            raise ValueError("API key is required")
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._transport = transport
        self._async_transport = async_transport

    def _coerce_options(self, options: ScreenshotOptionsInput) -> ScreenshotOptions:
        if isinstance(options, ScreenshotOptions):
            return options

        if not isinstance(options, MappingABC):
            raise TypeError("options must be a ScreenshotOptions instance or mapping")

        try:
            return ScreenshotOptions(**dict(options))  # type: ignore[arg-type]
        except TypeError as exc:
            raise ValueError(f"Invalid screenshot options: {exc}") from exc

    def _validate_options(self, options: ScreenshotOptions) -> None:
        if not options.url and not options.html:
            raise ValueError("Either url or html is required")

        if (options.geo_latitude is None) != (options.geo_longitude is None):
            raise ValueError("geo_latitude and geo_longitude must be provided together")

    def _format_query_value(self, value: object) -> str:
        if isinstance(value, bool):
            return str(value).lower()
        if isinstance(value, str):
            return value
        if isinstance(value, SequenceABC):
            return ",".join(str(item) for item in value)
        return str(value)

    def _set_param(self, params: Dict[str, str], key: str, value: object) -> None:
        if value is not None:
            params[key] = self._format_query_value(value)

    def _set_body_value(self, body: Dict[str, object], key: str, value: object) -> None:
        if value is not None:
            body[key] = value

    def _remove_elements_list(
        self, remove_elements: Optional[Sequence[str]]
    ) -> Optional[Sequence[str]]:
        if remove_elements is None:
            return None
        if isinstance(remove_elements, str):
            return [
                selector.strip()
                for selector in remove_elements.split(",")
                if selector.strip()
            ]
        return list(remove_elements)

    def _build_params(self, options: ScreenshotOptions) -> Dict[str, str]:
        params: Dict[str, str] = {}

        self._set_param(params, "url", options.url)
        self._set_param(params, "width", options.width)
        self._set_param(params, "height", options.height)
        self._set_param(params, "fullPage", options.full_page)
        self._set_param(params, "type", options.type)
        self._set_param(params, "quality", options.quality)
        self._set_param(params, "colorScheme", options.color_scheme)
        self._set_param(params, "waitUntil", options.wait_until)
        self._set_param(params, "waitForSelector", options.wait_for_selector)
        self._set_param(params, "delay", options.delay)
        self._set_param(params, "blockAds", options.block_ads)
        self._set_param(params, "removeCookieBanners", options.remove_cookie_banners)
        self._set_param(params, "cssInject", options.css_inject)
        self._set_param(params, "jsInject", options.js_inject)
        self._set_param(params, "stealthMode", options.stealth_mode)
        self._set_param(params, "devicePixelRatio", options.device_pixel_ratio)
        self._set_param(params, "timezone", options.timezone)
        self._set_param(params, "locale", options.locale)
        self._set_param(params, "cacheTtl", options.cache_ttl)
        self._set_param(params, "preloadFonts", options.preload_fonts)
        self._set_param(params, "removeElements", options.remove_elements)
        self._set_param(params, "removePopups", options.remove_popups)
        self._set_param(params, "mockupDevice", options.mockup_device)
        self._set_param(params, "geoLatitude", options.geo_latitude)
        self._set_param(params, "geoLongitude", options.geo_longitude)
        self._set_param(params, "geoAccuracy", options.geo_accuracy)
        return params

    def _build_body(self, options: ScreenshotOptions) -> Dict[str, object]:
        body: Dict[str, object] = {}

        self._set_body_value(body, "url", options.url)
        self._set_body_value(body, "html", options.html)
        self._set_body_value(body, "width", options.width)
        self._set_body_value(body, "height", options.height)
        self._set_body_value(body, "fullPage", options.full_page)
        self._set_body_value(body, "type", options.type)
        self._set_body_value(body, "quality", options.quality)
        self._set_body_value(body, "colorScheme", options.color_scheme)
        self._set_body_value(body, "waitUntil", options.wait_until)
        self._set_body_value(body, "waitForSelector", options.wait_for_selector)
        self._set_body_value(body, "delay", options.delay)
        self._set_body_value(body, "blockAds", options.block_ads)
        self._set_body_value(
            body,
            "removeCookieBanners",
            options.remove_cookie_banners,
        )
        self._set_body_value(body, "cssInject", options.css_inject)
        self._set_body_value(body, "jsInject", options.js_inject)
        self._set_body_value(body, "stealthMode", options.stealth_mode)
        self._set_body_value(body, "devicePixelRatio", options.device_pixel_ratio)
        self._set_body_value(body, "timezone", options.timezone)
        self._set_body_value(body, "locale", options.locale)
        self._set_body_value(body, "cacheTtl", options.cache_ttl)
        self._set_body_value(body, "preloadFonts", options.preload_fonts)
        self._set_body_value(
            body,
            "removeElements",
            self._remove_elements_list(options.remove_elements),
        )
        self._set_body_value(body, "removePopups", options.remove_popups)
        self._set_body_value(body, "mockupDevice", options.mockup_device)

        if options.geo_latitude is not None and options.geo_longitude is not None:
            geo_location: Dict[str, object] = {
                "latitude": options.geo_latitude,
                "longitude": options.geo_longitude,
            }
            self._set_body_value(geo_location, "accuracy", options.geo_accuracy)
            body["geoLocation"] = geo_location

        return body

    def _header_int(self, headers: httpx.Headers, key: str) -> int:
        value = headers.get(key)
        if value is None:
            return 0
        try:
            return int(value)
        except ValueError:
            return 0

    def _int_from_body(self, value: object) -> int:
        if value is None:
            return 0
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return 0
        try:
            return int(str(value))
        except (TypeError, ValueError):
            return 0

    def _parse_metadata(self, headers: httpx.Headers) -> ScreenshotMetadata:
        return ScreenshotMetadata(
            credits_remaining=self._header_int(headers, "x-credits-remaining"),
            screenshot_id=headers.get("x-screenshot-id", ""),
            duration_ms=self._header_int(headers, "x-duration-ms"),
        )

    def _handle_error(self, response: httpx.Response) -> NoReturn:
        try:
            body = response.json()
        except ValueError:
            raise ScreenshotAPIError(
                f"HTTP {response.status_code}: {response.reason_phrase}",
                response.status_code,
                "unknown_error",
            )

        if not isinstance(body, MappingABC):
            raise ScreenshotAPIError(
                f"HTTP {response.status_code}: {response.reason_phrase}",
                response.status_code,
                "unknown_error",
            )

        message = str(body.get("error", body.get("message", "Unknown error")))

        if response.status_code == 401:
            raise AuthenticationError(message)
        elif response.status_code == 402:
            balance = body.get("balance", body.get("creditBalance", 0))
            raise InsufficientCreditsError(message, self._int_from_body(balance))
        elif response.status_code == 403:
            raise InvalidAPIKeyError(message)
        elif response.status_code == 500:
            raise ScreenshotFailedError(
                str(body.get("message", body.get("error", "Screenshot failed")))
            )
        else:
            raise ScreenshotAPIError(message, response.status_code, "unknown_error")

    def screenshot(self, options: ScreenshotOptionsInput) -> ScreenshotResult:
        """Take a screenshot synchronously. Returns image bytes and metadata."""
        coerced = self._coerce_options(options)
        self._validate_options(coerced)

        try:
            with httpx.Client(
                timeout=self._timeout,
                transport=self._transport,
            ) as client:
                if coerced.html is not None:
                    response = client.post(
                        f"{self._base_url}/api/v1/screenshot",
                        json=self._build_body(coerced),
                        headers={"x-api-key": self._api_key},
                    )
                else:
                    response = client.get(
                        f"{self._base_url}/api/v1/screenshot",
                        params=self._build_params(coerced),
                        headers={"x-api-key": self._api_key},
                    )
        except httpx.RequestError as exc:
            raise NetworkError(f"Request failed: {exc}") from exc

        if response.status_code >= 400:
            self._handle_error(response)

        return ScreenshotResult(
            image=response.content,
            metadata=self._parse_metadata(response.headers),
            content_type=response.headers.get("content-type", "image/png"),
        )

    async def async_screenshot(
        self, options: ScreenshotOptionsInput
    ) -> ScreenshotResult:
        """Take a screenshot asynchronously. Returns image bytes and metadata."""
        coerced = self._coerce_options(options)
        self._validate_options(coerced)

        try:
            async with httpx.AsyncClient(
                timeout=self._timeout,
                transport=self._async_transport,
            ) as client:
                if coerced.html is not None:
                    response = await client.post(
                        f"{self._base_url}/api/v1/screenshot",
                        json=self._build_body(coerced),
                        headers={"x-api-key": self._api_key},
                    )
                else:
                    response = await client.get(
                        f"{self._base_url}/api/v1/screenshot",
                        params=self._build_params(coerced),
                        headers={"x-api-key": self._api_key},
                    )
        except httpx.RequestError as exc:
            raise NetworkError(f"Request failed: {exc}") from exc

        if response.status_code >= 400:
            self._handle_error(response)

        return ScreenshotResult(
            image=response.content,
            metadata=self._parse_metadata(response.headers),
            content_type=response.headers.get("content-type", "image/png"),
        )

    def save(
        self,
        options: ScreenshotOptionsInput,
        path: Union[str, Path],
    ) -> ScreenshotMetadata:
        """Take a screenshot and save it to a file. Returns metadata."""
        result = self.screenshot(options)
        Path(path).write_bytes(result.image)
        return result.metadata

    async def async_save(
        self,
        options: ScreenshotOptionsInput,
        path: Union[str, Path],
    ) -> ScreenshotMetadata:
        """Take a screenshot asynchronously and save it to a file."""
        result = await self.async_screenshot(options)
        Path(path).write_bytes(result.image)
        return result.metadata
