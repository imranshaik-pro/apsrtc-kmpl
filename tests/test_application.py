from src.reporting.application import build_daily_report


VEHICLE_HTML = """
<html>
<body>
<table class="demoTable">
<tr>
<th>SL</th>
<th>Log</th>
<th>Vehicle</th>
<th>Operation</th>
<th>Engine</th>
<th>Rev</th>
<th>NonRev</th>
<th>Total</th>
<th>HSD</th>
<th>KMPL</th>
<th>UpRev</th>
<th>UpNonRev</th>
<th>UpTotal</th>
<th>UpHSD</th>
<th>UpKMPL</th>
</tr>
<tr>
<td>1</td>
<td>LOG001</td>
<td>AP01A0001</td>
<td>ORD</td>
<td>HSD</td>
<td>100</td>
<td>0</td>
<td>145</td>
<td>41</td>
<td>3.54</td>
<td>700</td>
<td>0</td>
<td>1041</td>
<td>223</td>
<td>4.67</td>
</tr>
<tr>
<td>2</td>
<td>LOG002</td>
<td>AP01A0002</td>
<td>ORD</td>
<td>HSD</td>
<td>100</td>
<td>0</td>
<td>250</td>
<td>40</td>
<td>6.25</td>
<td>800</td>
<td>0</td>
<td>1500</td>
<td>250</td>
<td>6.00</td>
</tr>
</table>
</body>
</html>
"""


REGION_HTML = """
<html>
<body>
<table>
<tr>
<th>SLNO</th>
<th>Depot</th>
<th>Category</th>
<th>Target</th>
<th>Day Kms</th>
<th>UPD Kms</th>
<th>LYUD Kms</th>
<th>Variance</th>
<th>Month Kms</th>
<th>Day HSD</th>
<th>UPD HSD</th>
<th>LYUD HSD</th>
<th>Variance</th>
<th>Month HSD</th>
<th>Day KMPL</th>
<th>UPD KMPL</th>
<th>LYUD KMPL</th>
<th>Variance</th>
<th>Month KMPL</th>
<th>LMonth KMPL</th>
</tr>
<tr>
<td>1</td>
<td>PRODDUTUR</td>
<td>TOT</td>
<td>5.03</td>
<td>100</td>
<td>1000</td>
<td>900</td>
<td>0</td>
<td>1000</td>
<td>20</td>
<td>200</td>
<td>180</td>
<td>0</td>
<td>200</td>
<td>4.84</td>
<td>4.88</td>
<td>5.09</td>
<td>0</td>
<td>4.88</td>
<td>4.88</td>
</tr>
<tr>
<td></td>
<td></td>
<td>NAC</td>
<td>5.05</td>
<td>100</td>
<td>1000</td>
<td>900</td>
<td>0</td>
<td>1000</td>
<td>20</td>
<td>200</td>
<td>180</td>
<td>0</td>
<td>200</td>
<td>4.87</td>
<td>4.92</td>
<td>5.11</td>
<td>0</td>
<td>4.91</td>
<td>4.91</td>
</tr>
<tr>
<td></td>
<td></td>
<td>AC</td>
<td></td>
<td>100</td>
<td>1000</td>
<td>900</td>
<td>0</td>
<td>1000</td>
<td>20</td>
<td>200</td>
<td>180</td>
<td>0</td>
<td>200</td>
<td>3.68</td>
<td>3.73</td>
<td>4.11</td>
<td>0</td>
<td>3.73</td>
<td>3.79</td>
</tr>
</table>
</body>
</html>
"""


class FakeResponse:
    def __init__(self, text):
        self.text = text
        self.status_code = 200

    def raise_for_status(self):
        return None


class FakeSession:
    def __init__(self):
        self.calls = []

    def post(self, url, data, timeout):
        self.calls.append(
            {
                "method": "POST",
                "url": url,
                "data": data,
                "timeout": timeout,
            }
        )

        if "vehkmpl.php" in url:
            return FakeResponse(VEHICLE_HTML)

        raise AssertionError(
            f"Unexpected POST endpoint: {url}"
        )

    def get(self, url, params, timeout):
        self.calls.append(
            {
                "method": "GET",
                "url": url,
                "params": params,
                "timeout": timeout,
            }
        )

        if "achsd1.php" in url:
            return FakeResponse(REGION_HTML)

        raise AssertionError(
            f"Unexpected GET endpoint: {url}"
        )


def test_end_to_end_daily_report():
    session = FakeSession()

    report = build_daily_report(
        session=session,
        report_date="2026-08-18",
        depot="PRODDUTUR",
        vehicle_depot="PDTR/PRODDUTUR",
        region_code="YSRKADAPA",
    )

    assert "PRODDUTUR డిపో :: 18/08/2026 (మంగళవారం)" in report

    assert "ఈ రోజు            4.84      4.87      3.68" in report

    assert "ఈ రోజు వరకు       4.88      4.92      3.73" in report

    assert "(ఈ రోజు) :: 1>" in report

    assert "(ఈ రోజు వరకు) :: 1>" in report

    assert len(session.calls) == 2

    assert session.calls[0]["method"] == "POST"

    assert session.calls[0]["data"] == {
        "fyymm": "18/08/2026",
        "dept": "PDTR/PRODDUTUR",
    }

    assert session.calls[1]["method"] == "GET"

    assert session.calls[1]["params"] == {
        "action": "",
        "fdate": "2026-08-18",
        "rreg": "YSRKADAPA",
    }


print("Application integration tests passed.")
