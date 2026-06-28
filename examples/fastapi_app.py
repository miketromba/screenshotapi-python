from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException, Response

from screenshotapi import ScreenshotAPI, ScreenshotAPIError

app = FastAPI()
client = ScreenshotAPI(os.environ["SCREENSHOTAPI_KEY"])


@app.get("/screenshot")
def screenshot(url: str) -> Response:
    try:
        result = client.screenshot(
            {
                "url": url,
                "type": "webp",
                "width": 1440,
                "height": 900,
                "block_ads": True,
                "remove_cookie_banners": True,
            }
        )
    except ScreenshotAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return Response(content=result.image, media_type=result.content_type)
