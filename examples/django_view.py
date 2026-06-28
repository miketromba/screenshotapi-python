from __future__ import annotations

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse

from screenshotapi import ScreenshotAPI, ScreenshotAPIError


def screenshot_view(request: HttpRequest) -> HttpResponse:
    url = request.GET.get("url")
    if not url:
        return JsonResponse({"error": "url is required"}, status=400)

    client = ScreenshotAPI(settings.SCREENSHOTAPI_KEY)

    try:
        result = client.screenshot(
            {
                "url": url,
                "width": 1280,
                "height": 720,
                "type": "png",
                "cache_ttl": 3600,
            }
        )
    except ScreenshotAPIError as exc:
        return JsonResponse({"error": str(exc), "code": exc.code}, status=502)

    response = HttpResponse(result.image, content_type=result.content_type)
    response["x-screenshot-id"] = result.metadata.screenshot_id
    response["x-credits-remaining"] = str(result.metadata.credits_remaining)
    return response
