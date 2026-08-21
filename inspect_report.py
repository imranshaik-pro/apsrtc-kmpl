import sys
import re

sys.path.insert(0, "src")

from auth.client import login

session = login()

response = session.post(
    "http://103.44.14.20/med/vehkmpl.php",
    data={
        "fyymm": "18/08/2026",
        "dept": "PDTR/PRODDUTUR",
    },
    timeout=30,
)

table = re.search(
    r'<table[^>]*class="demoTable"[^>]*>(.*?)</table>',
    response.text,
    re.I | re.S,
)

rows = re.findall(
    r"<tr\b[^>]*>(.*?)</tr>",
    table.group(1),
    re.I | re.S,
) if table else []

print("Rows inside demoTable:", len(rows))
print(
    "Rows with 15 TDs:",
    sum(len(re.findall(r"<td\b", row, re.I)) == 15 for row in rows),
)
print(
    "Rows with other TD counts:",
    sorted(
        set(
            len(re.findall(r"<td\b", row, re.I))
            for row in rows
        )
    ),
)
