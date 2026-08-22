import requests
from bs4 import BeautifulSoup
from src.auth.client import login

session = login()
response = session.post(
    "http://103.44.14.20/med/vehkmpl.php",
    data={"fyymm": "18/08/2026", "dept": "KMPL"},
    timeout=30,
)
print("Status:", response.status_code)
print("URL:", response.url)
print("Content length:", len(response.text))
print("First 500 characters:")
print(response.text[:500])
with open("vehicle_response.html", "w", encoding="utf-8") as f:
    f.write(response.text)
print("Full HTML saved to vehicle_response.html")
