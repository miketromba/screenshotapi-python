# screenshotapi

Official typed Python SDK for
[ScreenshotAPI](https://screenshotapi.to?utm_source=pypi&utm_medium=python-sdk&utm_campaign=sdk-readme&ref=python-sdk),
the hosted screenshot API for turning URLs or HTML into PNG, JPEG, WebP, or PDF
captures.

## Install

```bash
pip install screenshotapi-to
```

Python 3.8+ is supported. The distribution package is `screenshotapi-to`, the
import package is `screenshotapi`, and the package ships `py.typed` metadata for
type checkers.

## Authentication

Create an API key in the ScreenshotAPI dashboard, then keep it in an environment
variable:

```bash
export SCREENSHOTAPI_KEY="sk_live_your_key_here"
```

The SDK sends your key in the `x-api-key` header. Keep API keys on the server;
do not expose them in browser bundles or mobile apps.

## First Screenshot

```python
import os

from screenshotapi import ScreenshotAPI

client = ScreenshotAPI(os.environ["SCREENSHOTAPI_KEY"])

metadata = client.save(
    {
        "url": "https://example.com",
        "width": 1440,
        "height": 900,
    },
    "screenshot.png",
)

print(f"Screenshot ID: {metadata.screenshot_id}")
print(f"Credits remaining: {metadata.credits_remaining}")
```

## Usage

### Initialize the Client

```python
from screenshotapi import ScreenshotAPI

client = ScreenshotAPI(
    "sk_live_your_key_here",
    base_url="https://screenshotapi.to",
    timeout=60.0,
)
```

### Capture Bytes

```python
from screenshotapi import ScreenshotOptions

result = client.screenshot(
    ScreenshotOptions(
        url="https://example.com",
        full_page=True,
        type="webp",
        quality=90,
        color_scheme="dark",
    )
)

image_bytes = result.image
content_type = result.content_type
credits_remaining = result.metadata.credits_remaining
```

Plain dictionaries are also supported:

```python
result = client.screenshot(
    {
        "url": "https://example.com",
        "full_page": True,
        "type": "webp",
    }
)
```

### Async Capture

```python
import asyncio
import os

from screenshotapi import ScreenshotAPI

client = ScreenshotAPI(os.environ["SCREENSHOTAPI_KEY"])


async def main() -> None:
    result = await client.async_screenshot({"url": "https://example.com"})
    print(f"Duration: {result.metadata.duration_ms}ms")

    await client.async_save({"url": "https://example.com"}, "screenshot.png")


asyncio.run(main())
```

## Advanced Options

```python
result = client.screenshot(
    {
        "url": "https://example.com/dashboard",
        "width": 1280,
        "height": 720,
        "device_pixel_ratio": 2,
        "full_page": False,
        "type": "webp",
        "quality": 85,
        "color_scheme": "dark",
        "wait_until": "networkidle0",
        "wait_for_selector": ".ready",
        "delay": 500,
        "block_ads": True,
        "remove_cookie_banners": True,
        "remove_popups": True,
        "remove_elements": [".newsletter", "#cookie-banner"],
        "css_inject": "body { caret-color: transparent; }",
        "js_inject": "window.scrollTo(0, 0)",
        "stealth_mode": True,
        "timezone": "America/New_York",
        "locale": "en-US",
        "cache_ttl": 3600,
        "preload_fonts": True,
        "geo_latitude": 40.7128,
        "geo_longitude": -74.0060,
        "geo_accuracy": 25,
    }
)
```

HTML rendering uses `POST /api/v1/screenshot` automatically:

```python
result = client.screenshot(
    {
        "html": "<html><body><h1>Invoice #123</h1></body></html>",
        "type": "pdf",
    }
)
```

Supported options:

| Python option | API parameter | Notes |
|---|---|---|
| `url` | `url` | Required unless `html` is provided |
| `html` | `html` | Raw HTML, sent with POST |
| `width`, `height` | `width`, `height` | Viewport size |
| `full_page` | `fullPage` | Capture full scrollable page |
| `type` | `type` | `png`, `jpeg`, `webp`, or `pdf` |
| `quality` | `quality` | JPEG/WebP quality, 1-100 |
| `color_scheme` | `colorScheme` | `light` or `dark` |
| `wait_until` | `waitUntil` | `load`, `domcontentloaded`, `networkidle0`, `networkidle2` |
| `wait_for_selector` | `waitForSelector` | CSS selector to wait for |
| `delay` | `delay` | Extra delay in milliseconds |
| `block_ads` | `blockAds` | Remove ads before capture |
| `remove_cookie_banners` | `removeCookieBanners` | Remove common consent banners |
| `css_inject`, `js_inject` | `cssInject`, `jsInject` | Inject CSS or JavaScript before capture |
| `stealth_mode` | `stealthMode` | Enable anti-bot fingerprint masking |
| `device_pixel_ratio` | `devicePixelRatio` | `1`, `2`, or `3` |
| `timezone`, `locale` | `timezone`, `locale` | Browser emulation settings |
| `cache_ttl` | `cacheTtl` | Cache identical captures for N seconds |
| `preload_fonts` | `preloadFonts` | Preload Google Fonts before capture |
| `remove_elements` | `removeElements` | CSS selectors to remove |
| `remove_popups` | `removePopups` | Remove common overlays and modals |
| `mockup_device` | `mockupDevice` | `browser`, `iphone`, or `macbook` frame |
| `geo_latitude`, `geo_longitude`, `geo_accuracy` | `geoLocation` or geo query params | Browser geolocation override |

## Error Handling

```python
from screenshotapi import (
    AuthenticationError,
    InsufficientCreditsError,
    InvalidAPIKeyError,
    NetworkError,
    ScreenshotAPI,
    ScreenshotAPIError,
    ScreenshotFailedError,
)

client = ScreenshotAPI("sk_live_your_key_here")

try:
    client.screenshot({"url": "https://example.com"})
except AuthenticationError:
    print("Missing API key")
except InvalidAPIKeyError:
    print("Invalid or revoked API key")
except InsufficientCreditsError as exc:
    print(f"No credits remaining. Balance: {exc.balance}")
except ScreenshotFailedError as exc:
    print(f"Screenshot failed: {exc}")
except NetworkError as exc:
    print(f"Could not reach ScreenshotAPI: {exc}")
except ScreenshotAPIError as exc:
    print(f"ScreenshotAPI error {exc.status} ({exc.code}): {exc}")
```

## Examples

Runnable examples live in `examples/`:

- `script_usage.py` for one-off scripts and cron jobs
- `fastapi_app.py` for FastAPI endpoints
- `django_view.py` for Django views
- `flask_app.py` for Flask routes

## Pricing and Free Tier

ScreenshotAPI includes
[200 free screenshots per month](https://screenshotapi.to/pricing?utm_source=pypi&utm_medium=python-sdk&utm_campaign=sdk-readme&ref=python-sdk)
with no credit card required. Paid subscriptions and credit packs are available
when you need more volume.

## Links

- [Documentation](https://screenshotapi.to/docs?utm_source=pypi&utm_medium=python-sdk&utm_campaign=sdk-readme&ref=python-sdk)
- [Screenshot API reference](https://screenshotapi.to/docs/api/screenshot?utm_source=pypi&utm_medium=python-sdk&utm_campaign=sdk-readme&ref=python-sdk)
- [Pricing](https://screenshotapi.to/pricing?utm_source=pypi&utm_medium=python-sdk&utm_campaign=sdk-readme&ref=python-sdk)
- [Support](mailto:support@screenshotapi.to?subject=Python%20SDK%20support)

## License

MIT
