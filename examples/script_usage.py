from __future__ import annotations

import os

from screenshotapi import (
    InsufficientCreditsError,
    ScreenshotAPI,
    ScreenshotAPIError,
)


def main() -> None:
    api_key = os.environ["SCREENSHOTAPI_KEY"]
    client = ScreenshotAPI(api_key)

    try:
        metadata = client.save(
            {
                "url": "https://example.com",
                "full_page": True,
                "type": "webp",
                "quality": 90,
            },
            "example.webp",
        )
    except InsufficientCreditsError as exc:
        print(f"No credits remaining. Balance: {exc.balance}")
        raise
    except ScreenshotAPIError as exc:
        print(f"ScreenshotAPI error ({exc.code}): {exc}")
        raise

    print(f"Saved example.webp as {metadata.screenshot_id}")
    print(f"Credits remaining: {metadata.credits_remaining}")


if __name__ == "__main__":
    main()
