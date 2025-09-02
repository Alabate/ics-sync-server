import os
import re
from flask import Response

def check_url_key(url_key: str) -> int | Response:
    """Check if the given url_key is valid.

    If it's valid it return the id of the user and you can continue.
    If invalid it return a Reponse with a 401 error, you should return it.

    Args:
        url_key (str): Key that has been given in the URL
    """
    # Check for environment variables like URL_KEY_1, URL_KEY_2, etc.
    for key, value in os.environ.items():
        # Use regex to match keys that follow the pattern URL_KEY_<number>
        match = re.match(r"URL_KEY_(\d+)$", key)
        if match and value == url_key:
            # Extract the user ID from the captured group
            user_id = int(match.group(1))
            return user_id

    # If no matching key found, return unauthorized
    return Response("Unauthorized", status=401, content_type="text/plain")
