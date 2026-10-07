"""Verified APSRTC monthly range counts, with separate durable FY history.

These are source classifications, not buckets recalculated from daily KMPL.
The existing workbook/Sheets serializers are deliberately reused.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from datetime import date, datetime

from bs4 import BeautifulSoup
import report_details as d

CACHE_TITLE = "_KMPL_RANGE_HISTORY"
SCHEMA = "kmpl-range-2"
MONTHLY_TITLE = "KMPL Range Distribution"
ANNUAL_TITLE = "FY KMPL Range Trend"
ENDPOINTS = {"VEHICLE": "vehlog_kmpldepot.php", "DRIVER": "drvlog_kmpldepot.php"}
UPTO_SELECTORS = {"VEHICLE": "vehlog_kmpl.php", "DRIVER": "drvlog_ckmpl.php"}
UPTO_ENDPOINTS = {"VEHICLE": "vehlog_kmpldepot.php", "DRIVER": "drvlog_ckmpldepot.php"}
SCOPES = ("MONTH", "UPTO")
LABELS = ("Below -3.00", "3.00 - 4.00", "4.01 - 5.00", "5.01 - 5.15",
          "5.16 - 5.30", "5.31 - 5.60", "5.60 - ABV")
HEADER_KEYS = tuple(d.key(x) for x in LABELS) + ("GTOTAL",)


def count(value):
    text = str(value).strip().replace(",", "")
    if not re.fullmatch(r"\d+", text):
        raise ValueError(f"Range count must be a non-negative integer: {value!r}")
    return int(text)


def parse_range(html, entity, depot, period, region, scope="MONTH"):
    if entity not in ENDPOINTS:
        raise ValueError("Unknown range source")
    soup = BeautifulSoup(html, "html.parser")
    headings = [d.norm(h.get_text(" ", strip=True)) for h in soup.find_all(re.compile(r"^h[1-6]$"))]
    expected = d.month_end(period).strftime("%m/%Y")
    if not any(re.search(rf"RANGE WISE {entity} HSD KMPL FOR THE MONTH OF:\s*{expected}\s*$", h)
               for h in headings):
        raise ValueError("Range source entity/month heading is not verified")
    choices = []
    for table in soup.find_all("table"):
        trs = table.find_all("tr")
        if len(trs) < 3:
            continue
        first = trs[0].find_all(["th", "td"], recursive=False)
        second = trs[1].find_all(["th", "td"], recursive=False)
        if len(first) != 3 or len(second) != 8:
            continue
        if (d.key(first[0].get_text()) != "SLNO" or d.key(first[1].get_text()) not in ("REGION", "DEPOT")
                or first[0].get("rowspan") != "2" or first[1].get("rowspan") != "2"
                or first[2].get("colspan") != "8"
                or d.key(first[2].get_text()) != f"KMPLRANGEWISENOOF{entity}S"
                or tuple(d.key(c.get_text(" ", strip=True)) for c in second) != HEADER_KEYS):
            continue
        rows, seen, total = [], set(), None
        for tr in trs[2:]:
            cells = tr.find_all(["td", "th"], recursive=False)
            if len(cells) != 10:
                raise ValueError("Range row width does not match source headings")
            values = [c.get_text(" ", strip=True) for c in cells]
            counts = [count(v) for v in values[2:]]
            if sum(counts[:7]) != counts[7]:
                raise ValueError("Range row does not reconcile to G.Total")
            name = d.norm(values[1])
            if name == "TOTAL":
                if total is not None or tr is not trs[-1]:
                    raise ValueError("Expected one final regional total")
                total = counts
            else:
                if not re.fullmatch(r"\d+", values[0]) or not name or name in seen or total is not None:
                    raise ValueError("Duplicate/invalid depot range identity")
                link = cells[1].find("a", href=True)
                if link:
                    from urllib.parse import parse_qs, urlparse
                    query = parse_qs(urlparse(link["href"]).query)
                    if query.get("yymm") != [period.replace("-", "")] or query.get("rreg") != [name]:
                        raise ValueError("Range drilldown depot/month does not match its row")
                seen.add(name)
                rows.append([int(values[0]), name, *counts])
        if not rows or total is None or any(sum(row[i+2] for row in rows) != total[i] for i in range(8)):
            raise ValueError("Regional range totals do not reconcile")
        selected = [row for row in rows if row[1] == d.norm(depot)]
        if len(selected) != 1:
            raise ValueError("No unique exact selected-depot range row")
        choices.append(dict(depot=d.norm(depot), period=period, entity=entity, scope=scope, region=region,
                            headers=["SL No", "Depot", *[c.get_text(" ", strip=True) for c in second]],
                            rows=rows, regional_total=total, counts=selected[0][2:],
                            source=f"{d.BASE}/med/{(ENDPOINTS if scope == 'MONTH' else UPTO_ENDPOINTS)[entity]}"))
    if len(choices) != 1:
        layouts=[]
        for table in soup.find_all("table"):
            layouts.append([[dict(text=c.get_text(" ",strip=True),key=d.key(c.get_text()),rowspan=c.get("rowspan"),colspan=c.get("colspan"))
                             for c in tr.find_all(["th","td"],recursive=False)] for tr in table.find_all("tr")[:2]])
        raise ValueError("Expected one verified range table; empty/login pages are unavailable; expected="+str((entity,HEADER_KEYS))+"; headers="+json.dumps(layouts))
    return choices[0]


class SourceAdapter:
    def __init__(self, session, depot, region, today=None):
        self.session, self.depot, self.region = session, depot, region
        self.today = today or datetime.now(d.IST).date()

    def __call__(self, entity, period, scope="MONTH"):
        if scope not in SCOPES:
            raise ValueError("Unknown range scope")
        if d.month_end(period).replace(day=1) > self.today:
            raise ValueError("Future range months are not requested")
        payload = dict(action="", yymm=period.replace("-", ""), rreg=self.region)
        # The owner-verified Vehicle Upto selector posts to the same depot result endpoint
        # as Vehicle Month; visiting the selector first preserves the APSRTC source flow.
        if scope == "UPTO":
            selector = self.session.get(f"{d.BASE}/med/{UPTO_SELECTORS[entity]}", timeout=45)
            selector.raise_for_status()
        endpoint = (ENDPOINTS if scope == "MONTH" else UPTO_ENDPOINTS)[entity]
        response = self.session.get(f"{d.BASE}/med/{endpoint}", params=payload, timeout=45)
        response.raise_for_status()
        snap = parse_range(response.text, entity, self.depot, period, self.region, scope)
        snap.update(request=payload, fetched_at=datetime.now(d.IST).isoformat(timespec="seconds"),
                    provisional=d.month_end(period) >= self.today)
        return snap
def update(cache, periods, fetch, selected, checkpoint=lambda: None, include_upto=False):
    calls = []
    for period in periods:
        d.month_end(period)
        groups = cache["months"].setdefault(period, {})
        scopes = SCOPES if include_upto and period == selected else ("MONTH",)
        for entity in ENDPOINTS:
            for scope in scopes:
                key = f"{entity}_{scope}"
                old = groups.get(key) or (groups.get(entity) if scope == "MONTH" else None)
                if old and not old.get("provisional") and period != selected:
                    groups[key] = old
                    continue
                calls.append((entity, period, scope))
                try:
                    snap = validate_snapshot(fetch(entity, period, scope), cache["depot"], entity, period, scope)
                    groups[key] = copy.deepcopy(snap)
                    cache["errors"].get(period, {}).pop(key, None)
                except Exception as exc:
                    cache["errors"].setdefault(period, {})[key] = f"{type(exc).__name__}: {exc}"[:300]
                    print(f"RANGE_SOURCE_UNAVAILABLE {cache['depot']} {period} {entity} {scope}: {exc}")
        checkpoint()
    return calls

