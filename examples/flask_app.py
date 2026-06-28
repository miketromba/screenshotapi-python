from __future__ import annotations

import os

from flask import Flask, Response, jsonify, request

from screenshotapi import ScreenshotAPI, ScreenshotAPIError

app = Flask(__name__)
client = ScreenshotAPI(os.environ["SCREENSHOTAPI_KEY"])


@app.get("/screenshot")
def screenshot() -> Response:
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "url is required"}), 400

    try:
        result = client.screenshot(
            {
                "url": url,
                "full_page": request.args.get("full_page") == "true",
                "type": "jpeg",
                "quality": 85,
            }
        )
    except ScreenshotAPIError as exc:
        return jsonify({"error": str(exc), "code": exc.code}), 502

    return Response(result.image, mimetype=result.content_type)
