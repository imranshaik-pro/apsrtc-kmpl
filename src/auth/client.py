import requests

from src.config.settings import APSRTC_PASSWORD, APSRTC_USERNAME


LOGIN_URL = "http://103.44.14.20/index.php"


def login() -> requests.Session:
    session = requests.Session()

    response = session.post(
        LOGIN_URL,
        data={
            "username": APSRTC_USERNAME,
            "password": APSRTC_PASSWORD,
            "Login": "Login",
        },
        allow_redirects=True,
        timeout=30,
    )

    response.raise_for_status()

    if "PHPSESSID" not in session.cookies:
        raise RuntimeError(
            "Login did not establish a PHP session."
        )

    print(f"Login HTTP status: {response.status_code}")
    print(f"Final URL: {response.url}")
    print("PHP session established: YES")

    return session
