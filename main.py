from pages.ucpa import get_content as get_ucpa_ics_content
from utils import check_url_key
from dotenv import load_dotenv
from flask import Flask, Response
from flask_caching import Cache
import os

load_dotenv()
app = Flask(__name__)
cache = Cache(app, config={"CACHE_TYPE": "SimpleCache"})


@app.route("/healthcheck", methods=["GET"])
def healthcheck():
    """Health check endpoint needed for kubernetes probes."""
    return Response("OK", status=200, content_type="text/plain")


@app.route("/<url_key>/ucpa.ics", methods=["GET"])
@cache.cached(timeout=300)
def ucpa_ics(url_key):
    """Serve the UCPA reservation calendar ICS file."""
    url_key_response = check_url_key(url_key)
    if not isinstance(url_key_response, int):
        return url_key_response

    return Response(
        get_ucpa_ics_content(url_key_response),
        status=200,
        content_type="text/plain",  # Should be "text/calendar" but it's harder to debug
        headers={"Content-Disposition": "inline; filename=ucpa.ics"},
    )


if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT, debug=True)
