from decimal import Decimal
from pathlib import Path

from src.parser.region_parser import parse_region_file, parse_region_html


TEST_HTML = """
<html>
<body>

<table border="1">

<tr>
    <th>SLNO</th>
    <th>Depot</th>
    <th>TOT/NAC</th>
    <th>Target KMPL</th>
    <th>Day Kms</th>
    <th>UPD Kms</th>
    <th>LYUD Kms</th>
    <th>Variance</th>
    <th>Up to Month Kms</th>
    <th>Day Hsd</th>
    <th>UPD Hsd</th>
    <th>LYUD Hsd</th>
    <th>Variance</th>
    <th>Up to Month Hsd</th>
    <th>Day KMPL</th>
    <th>UPD KMPL</th>
    <th>LYUD KMPL</th>
    <th>Variance</th>
    <th>Up to Month KMPL</th>
    <th>LMonth KMPL</th>
</tr>

<tr>
    <td rowspan="3">1</td>
    <td rowspan="3">KADAPA</td>
    <td>TOT</td>
    <td>4.90</td>
    <td>41360</td>
    <td>684013</td>
    <td>643952</td>
    <td>122332</td>
    <td>5201281</td>
    <td>8733</td>
    <td>145694</td>
    <td>134978</td>
    <td>10716</td>
    <td>1121379</td>
    <td>4.74</td>
    <td>4.69</td>
    <td>4.77</td>
    <td>-0.08</td>
    <td>4.64</td>
    <td>4.62</td>
</tr>

<tr>
    <td>NAC</td>
    <td>5.16</td>
    <td>37262</td>
    <td>603317</td>
    <td>561681</td>
    <td>41636</td>
    <td>4582425</td>
    <td>7480</td>
    <td>121250</td>
    <td>111033</td>
    <td>10217</td>
    <td>927314</td>
    <td>4.98</td>
    <td>4.98</td>
    <td>5.06</td>
    <td>-0.08</td>
    <td>4.94</td>
    <td>4.93</td>
</tr>

<tr>
    <td>AC</td>
    <td></td>
    <td>4098</td>
    <td>80696</td>
    <td>82271</td>
    <td>-1575</td>
    <td>618856</td>
    <td>1253</td>
    <td>24444</td>
    <td>23945</td>
    <td>499</td>
    <td>194065</td>
    <td>3.27</td>
    <td>3.30</td>
    <td>3.44</td>
    <td>-0.14</td>
    <td>3.19</td>
    <td>3.15</td>
</tr>

<tr>
    <td>2</td>
    <td>MYDUKUR</td>
    <td>TOT</td>
    <td>5.22</td>
    <td>13415</td>
    <td>219600</td>
    <td>214567</td>
    <td>5033</td>
    <td>1689644</td>
    <td>2563</td>
    <td>41500</td>
    <td>40620</td>
    <td>880</td>
    <td>316938</td>
    <td>5.23</td>
    <td>5.29</td>
    <td>5.28</td>
    <td>0.01</td>
    <td>5.33</td>
    <td>5.35</td>
</tr>

</table>

</body>
</html>
"""


def test_region_parser():
    records = parse_region_html(TEST_HTML)

    assert len(records) == 4

    kadapa_tot = records[0]

    assert kadapa_tot["slno"] == 1
    assert kadapa_tot["depot"] == "KADAPA"
    assert kadapa_tot["category"] == "TOT"
    assert kadapa_tot["target_kmpl"] == Decimal("4.90")
    assert kadapa_tot["day_kmpl"] == Decimal("4.74")
    assert kadapa_tot["upd_kmpl"] == Decimal("4.69")
    assert kadapa_tot["lyud_kmpl"] == Decimal("4.77")
    assert kadapa_tot["up_to_month_kmpl"] == Decimal("4.64")
    assert kadapa_tot["lmonth_kmpl"] == Decimal("4.62")

    kadapa_nac = records[1]

    assert kadapa_nac["slno"] == 1
    assert kadapa_nac["depot"] == "KADAPA"
    assert kadapa_nac["category"] == "NAC"
    assert kadapa_nac["target_kmpl"] == Decimal("5.16")
    assert kadapa_nac["day_kmpl"] == Decimal("4.98")
    assert kadapa_nac["upd_kmpl"] == Decimal("4.98")
    assert kadapa_nac["lyud_kmpl"] == Decimal("5.06")
    assert kadapa_nac["lmonth_kmpl"] == Decimal("4.93")

    kadapa_ac = records[2]

    assert kadapa_ac["slno"] == 1
    assert kadapa_ac["depot"] == "KADAPA"
    assert kadapa_ac["category"] == "AC"
    assert kadapa_ac["target_kmpl"] is None
    assert kadapa_ac["day_kmpl"] == Decimal("3.27")
    assert kadapa_ac["upd_kmpl"] == Decimal("3.30")
    assert kadapa_ac["lyud_kmpl"] == Decimal("3.44")
    assert kadapa_ac["lmonth_kmpl"] == Decimal("3.15")

    mydukur = records[3]

    assert mydukur["slno"] == 2
    assert mydukur["depot"] == "MYDUKUR"
    assert mydukur["category"] == "TOT"
    assert mydukur["target_kmpl"] == Decimal("5.22")
    assert mydukur["day_kmpl"] == Decimal("5.23")
    assert mydukur["upd_kmpl"] == Decimal("5.29")
    assert mydukur["lyud_kmpl"] == Decimal("5.28")
    assert mydukur["lmonth_kmpl"] == Decimal("5.35")


def test_real_region_response():
    response_file = Path("region_response.html")

    assert response_file.exists(), (
        "region_response.html was not found in the project root."
    )

    records = parse_region_file(response_file)

    assert len(records) == 11

    proddutur_records = [
        record
        for record in records
        if record["depot"] == "PRODDUTUR"
    ]

    assert len(proddutur_records) == 3

    proddutur_tot = next(
        record
        for record in proddutur_records
        if record["category"] == "TOT"
    )

    proddutur_nac = next(
        record
        for record in proddutur_records
        if record["category"] == "NAC"
    )

    proddutur_ac = next(
        record
        for record in proddutur_records
        if record["category"] == "AC"
    )

    assert proddutur_tot["target_kmpl"] == Decimal("5.03")
    assert proddutur_tot["day_kmpl"] == Decimal("4.84")
    assert proddutur_tot["upd_kmpl"] == Decimal("4.88")
    assert proddutur_tot["lyud_kmpl"] == Decimal("5.09")
    assert proddutur_tot["lmonth_kmpl"] == Decimal("4.88")

    assert proddutur_nac["target_kmpl"] == Decimal("5.05")
    assert proddutur_nac["day_kmpl"] == Decimal("4.87")
    assert proddutur_nac["upd_kmpl"] == Decimal("4.92")
    assert proddutur_nac["lyud_kmpl"] == Decimal("5.11")
    assert proddutur_nac["lmonth_kmpl"] == Decimal("4.91")

    assert proddutur_ac["target_kmpl"] is None
    assert proddutur_ac["day_kmpl"] == Decimal("3.68")
    assert proddutur_ac["upd_kmpl"] == Decimal("3.73")
    assert proddutur_ac["lyud_kmpl"] == Decimal("4.11")
    assert proddutur_ac["lmonth_kmpl"] == Decimal("3.79")


if __name__ == "__main__":
    test_region_parser()
    test_real_region_response()
    print("Region parser tests passed.")