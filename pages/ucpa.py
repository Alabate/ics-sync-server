import re
import requests
from urllib.parse import urlencode
import time
import os
from ics import Calendar, Event
import base64
import json


def get_oauth2_cookie(user_id: int):
    """
    We first need to get an OAuth2 cookie to access the UCPA API.

    login.ucpa.com is an oauth2 provider, and www.ucpa.com/sport-station/espacepersonnel
    is an oauth2 client. We will simulate being the client to get the cookie.

    The login is a simple form with a CSRF token. So we first need to get the
    CSRF token from the login page, then we can perform the login.
    """
    # Get credentials from environment variables
    username = os.getenv(f"UCPA_USERNAME_{user_id}")
    password = os.getenv(f"UCPA_PASSWORD_{user_id}")
    assert (
        username and password
    ), f"Missing UCPA_USERNAME_{user_id} or UCPA_PASSWORD_{user_id} environment variables."

    # Create the auth url that will be used for the two steps
    login_params = {
        "client_id": "15qf9khc3hb392j10im7t1179f",
        "redirect_uri": "https://www.ucpa.com/sport-station/espacepersonnel/af/authorize",
        "response_type": "code",
        "scope": "openid profile email phone",
        "state": base64.b64encode(
            json.dumps(
                {
                    "returnUrl": "https://www.ucpa.com/sport-station/espacepersonnel/nantes/accueil",
                    "partner": "alpha",
                }
            ).encode('utf-8')
        ),
    }
    login_url = f"https://login.ucpa.com/authorize?{urlencode(login_params)}"

    # Step 1: Get login page to extract CSRF token
    print("Step 1: Get login page to extract CSRF token..")
    session = requests.Session()
    response = session.get(login_url)

    if response.status_code != 200:
        print("Response status:", response.status_code)
        print("Response headers:", response.headers)
        print("Response text:", response.text)
        raise Exception("Failed to retrieve login page.")
    print("   Done. Status code:", response.status_code)

    # Extract CSRF token using regex
    print("Extract CSRF token using regex..")
    match = re.search(r'name="_csrf_token" value="(.*?)"', response.text)

    if not match:
        print("Response status:", response.status_code)
        print("Response headers:", response.headers)
        print("Response text:", response.text)
        raise Exception("CSRF token not found in response.")

    csrf_token = match.group(1)
    print("   Done. CSRF token length:", len(csrf_token))

    # Step 2: Perform login
    print("Step 2: Perform login to get OAuth2 cookie..")
    login_data = {
        "_csrf_token": csrf_token,
        "username": username,
        "password": password,
        "signin_context": "",
        "submit": "Se connecter",
    }
    login_response = session.post(login_url, data=login_data)

    if "oauth2_cookie" in session.cookies:
        print("   Done. Oauth2 cookie length:", len(session.cookies["oauth2_cookie"]))
        return session.cookies["oauth2_cookie"]
    else:
        print("Response status:", response.status_code)
        print("Response headers:", response.headers)
        print("Response text:", response.text)
        raise Exception("OAuth2 cookie not found in response.")


def get_scheduled_reservations(oauth2_cookie):
    """
    All scheduled reservations are retrieved in json from the UCPA API now that
    we have the OAuth2 cookie.
    """
    url = (
        "https://www.ucpa.com/sport-station/espacepersonnel/api/reservations/scheduled"
    )
    headers = {
        "content-type": "application/json",
        "cookie": f"oauth2_cookie={oauth2_cookie}",
    }
    payload = {"workspace": "alpha_nan", "source": "legacy"}
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print("Response status:", response.status_code)
        print("Response headers:", response.headers)
        print("Response text:", response.text)
        raise Exception("Failed to retrieve scheduled reservations.")


def convert_reservations_to_ics(data) -> str:
    """Convert the JSON from the UCPA API to an ICS file using the `ics` library."""
    if not data or not data.get("success"):
        print("Data:", data)
        raise Exception("Invalid data format.")

    calendar = Calendar()

    for customer in data.get("data", []):
        for session in customer.get("sessions", []):
            start_time = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.gmtime(session.get("startTimestamp") / 1000)
            )
            end_time = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.gmtime(session.get("endTimestamp") / 1000)
            )
            event_name = f"{session.get('type', 'Activity')} - UCPA"

            event = Event()
            event.name = event_name
            event.begin = start_time
            event.end = end_time
            event.uid = f"{session.get('qrcode')}-{session.get('activityCode')}-{session.get('startTimestamp')}@ucpa.com"
            event.location = "UCPA Nantes, 9 Bd de Berlin, 44000 Nantes"

            calendar.events.add(event)

    return calendar.serialize()


def get_content(user_id: int) -> bytes:
    oauth2_cookie = get_oauth2_cookie(user_id)
    reservations = get_scheduled_reservations(oauth2_cookie)
    ics = convert_reservations_to_ics(reservations)
    return ics.encode("utf-8")
