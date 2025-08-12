import os
from flask import Response

def check_url_key(url_key: str) -> None | Response:
    """Check if the given url_key is valid.

    If it's valid it return None and you can continue.
    If invalid it return a Reponse with a 401 error, you should return it.

    Args:
        url_key (str): Key that has been given in the URL
    """
    conf_url_key = os.getenv("URL_KEY")
    if conf_url_key is None or conf_url_key == "":
        raise Exception("Please configure the URL_KEY environement variable on this server.")
    
    if conf_url_key != url_key:
        return Response("Unauthorized", status=401, content_type="text/plain")
