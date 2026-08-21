import os

from dotenv import load_dotenv

load_dotenv()

APSRTC_USERNAME = os.getenv("APSRTC_USERNAME")
APSRTC_PASSWORD = os.getenv("APSRTC_PASSWORD")

if not APSRTC_USERNAME or not APSRTC_PASSWORD:
    raise RuntimeError(
        "APSRTC_USERNAME and APSRTC_PASSWORD must be set in .env"
    )
