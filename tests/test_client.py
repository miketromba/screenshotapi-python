from __future__ import annotations

import json
from pathlib import Path
from typing import List

import httpx
import pytest

from screenshotapi import (
    AuthenticationError,
    InsufficientCreditsError,
    InvalidAPIKeyError,
    NetworkError,
    ScreenshotAPI,
    ScreenshotAPIError,
    ScreenshotFailedError,
    ScreenshotOptions,
)

TEST_KEY = "sk_test_abc123"
IMAGE_BYTES = b"fake-image"


def success_response(
    content_type: str = "image/png",
    credits_remaining: str = "950",
    screenshot_id: str = "ss_abc",
    duration_ms: str = "1234",
) -> httpx.Response:
    return httpx.Response(
        200,
        content=IMAGE_BYTES,
        headers={
            "content-type": content_type,
            "x-credits-remaining": credits_remaining,
            "x-screenshot-id": screenshot_id,
            "x-duration-ms": duration_ms,
        },
    )


def json_error(status_code: int, body: dict[str, object]) -> httpx.Response:
    return httpx.Response(status_code, json=body)


def client_with_handler(
    handler: httpx.MockTransport,
) -> ScreenshotAPI:
    return ScreenshotAPI(
        TEST_KEY,
        base_url="https://unit.test/",
        transport=handler,
        async_transport=handler,
    )


def test_constructor_requires_api_key() -> None:
    with pytest.raises(ValueError, match="API key is required"):
        ScreenshotAPI("")


def test_get_screenshot_builds_expected_request() -> None:
    requests: List[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return success_response("image/webp", "800", "ss_xyz", "2345")

    client = client_with_handler(httpx.MockTransport(handler))

    result = client.screenshot(
        ScreenshotOptions(
            url="https://example.com",
            width=1280,
            height=720,
            full_page=True,
            type="webp",
            quality=80,
            color_scheme="dark",
            wait_until="networkidle0",
            wait_for_selector="#main",
            delay=500,
            block_ads=True,
            remove_cookie_banners=True,
            css_inject="body{background:white}",
            js_inject="window.ready=true",
            stealth_mode=True,
            device_pixel_ratio=2,
            timezone="America/Chicago",
            locale="en-US",
            cache_ttl=3600,
            preload_fonts=True,
            remove_elements=[".popup", "#banner"],
            remove_popups=True,
            mockup_device="browser",
            geo_latitude=41.881832,
            geo_longitude=-87.623177,
            geo_accuracy=20,
        )
    )

    request = requests[0]
    params = dict(request.url.params)

    assert request.method == "GET"
    assert str(request.url).startswith("https://unit.test/api/v1/screenshot")
    assert request.headers["x-api-key"] == TEST_KEY
    assert params["url"] == "https://example.com"
    assert params["width"] == "1280"
    assert params["height"] == "720"
    assert params["fullPage"] == "true"
    assert params["type"] == "webp"
    assert params["quality"] == "80"
    assert params["colorScheme"] == "dark"
    assert params["waitUntil"] == "networkidle0"
    assert params["waitForSelector"] == "#main"
    assert params["delay"] == "500"
    assert params["blockAds"] == "true"
    assert params["removeCookieBanners"] == "true"
    assert params["cssInject"] == "body{background:white}"
    assert params["jsInject"] == "window.ready=true"
    assert params["stealthMode"] == "true"
    assert params["devicePixelRatio"] == "2"
    assert params["timezone"] == "America/Chicago"
    assert params["locale"] == "en-US"
    assert params["cacheTtl"] == "3600"
    assert params["preloadFonts"] == "true"
    assert params["removeElements"] == ".popup,#banner"
    assert params["removePopups"] == "true"
    assert params["mockupDevice"] == "browser"
    assert params["geoLatitude"] == "41.881832"
    assert params["geoLongitude"] == "-87.623177"
    assert params["geoAccuracy"] == "20"
    assert result.image == IMAGE_BYTES
    assert result.content_type == "image/webp"
    assert result.metadata.credits_remaining == 800
    assert result.metadata.screenshot_id == "ss_xyz"
    assert result.metadata.duration_ms == 2345


def test_dict_options_omit_unset_optional_params() -> None:
    requests: List[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return success_response()

    client = client_with_handler(httpx.MockTransport(handler))
    client.screenshot({"url": "https://example.com"})

    params = dict(requests[0].url.params)
    assert params == {"url": "https://example.com"}


def test_html_uses_post_json_body() -> None:
    requests: List[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return success_response("image/png")

    client = client_with_handler(httpx.MockTransport(handler))
    client.screenshot(
        {
            "html": "<html><body>Hello</body></html>",
            "type": "png",
            "remove_elements": [".ad"],
            "geo_latitude": 40.0,
            "geo_longitude": -75.0,
        }
    )

    request = requests[0]
    assert request.method == "POST"
    assert request.url.path == "/api/v1/screenshot"
    assert request.headers["x-api-key"] == TEST_KEY
    assert request.headers["content-type"] == "application/json"
    assert json.loads(request.read()) == {
        "html": "<html><body>Hello</body></html>",
        "type": "png",
        "removeElements": [".ad"],
        "geoLocation": {"latitude": 40.0, "longitude": -75.0},
    }


def test_save_writes_file_and_returns_metadata(tmp_path: Path) -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return success_response()

    output = tmp_path / "screenshot.png"
    client = client_with_handler(httpx.MockTransport(handler))
    metadata = client.save({"url": "https://example.com"}, output)

    assert output.read_bytes() == IMAGE_BYTES
    assert metadata.screenshot_id == "ss_abc"


def test_missing_url_and_html_raises_before_request() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        raise AssertionError("request should not be sent")

    client = client_with_handler(httpx.MockTransport(handler))

    with pytest.raises(ValueError, match="Either url or html is required"):
        client.screenshot({})


def test_partial_geolocation_raises_before_request() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        raise AssertionError("request should not be sent")

    client = client_with_handler(httpx.MockTransport(handler))

    with pytest.raises(ValueError, match="geo_latitude and geo_longitude"):
        client.screenshot({"url": "https://example.com", "geo_latitude": 40.0})


@pytest.mark.parametrize(
    ("status_code", "body", "error_type", "code"),
    [
        (
            401,
            {"error": "API key required"},
            AuthenticationError,
            "authentication_error",
        ),
        (
            402,
            {"error": "Insufficient quota", "creditBalance": 7},
            InsufficientCreditsError,
            "insufficient_credits",
        ),
        (403, {"error": "Invalid API key"}, InvalidAPIKeyError, "invalid_api_key"),
        (
            500,
            {"message": "Render timed out"},
            ScreenshotFailedError,
            "screenshot_failed",
        ),
    ],
)
def test_known_error_responses_raise_specific_exceptions(
    status_code: int,
    body: dict[str, object],
    error_type: type[ScreenshotAPIError],
    code: str,
) -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return json_error(status_code, body)

    client = client_with_handler(httpx.MockTransport(handler))

    with pytest.raises(error_type) as exc_info:
        client.screenshot({"url": "https://example.com"})

    assert exc_info.value.status == status_code
    assert exc_info.value.code == code
    if isinstance(exc_info.value, InsufficientCreditsError):
        assert exc_info.value.balance == 7


def test_unknown_json_error_raises_base_error() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return json_error(429, {"message": "Rate limited"})

    client = client_with_handler(httpx.MockTransport(handler))

    with pytest.raises(ScreenshotAPIError) as exc_info:
        client.screenshot({"url": "https://example.com"})

    assert exc_info.value.status == 429
    assert exc_info.value.code == "unknown_error"
    assert str(exc_info.value) == "Rate limited"


def test_non_json_error_raises_base_error() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            502,
            content=b"Bad Gateway",
        )

    client = client_with_handler(httpx.MockTransport(handler))

    with pytest.raises(ScreenshotAPIError) as exc_info:
        client.screenshot({"url": "https://example.com"})

    assert exc_info.value.status == 502
    assert exc_info.value.code == "unknown_error"
    assert "HTTP 502" in str(exc_info.value)


def test_invalid_metadata_headers_default_to_zero() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return success_response(credits_remaining="n/a", duration_ms="slow")

    client = client_with_handler(httpx.MockTransport(handler))
    result = client.screenshot({"url": "https://example.com"})

    assert result.metadata.credits_remaining == 0
    assert result.metadata.duration_ms == 0


def test_request_errors_are_wrapped() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    client = client_with_handler(httpx.MockTransport(handler))

    with pytest.raises(NetworkError) as exc_info:
        client.screenshot({"url": "https://example.com"})

    assert exc_info.value.status == 0
    assert exc_info.value.code == "network_error"


async def test_async_screenshot_uses_async_transport() -> None:
    requests: List[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return success_response("application/pdf")

    transport = httpx.MockTransport(handler)
    client = ScreenshotAPI(
        TEST_KEY,
        base_url="https://unit.test",
        async_transport=transport,
    )

    result = await client.async_screenshot(
        {"url": "https://example.com", "type": "pdf"}
    )

    assert requests[0].method == "GET"
    assert dict(requests[0].url.params)["type"] == "pdf"
    assert result.content_type == "application/pdf"
