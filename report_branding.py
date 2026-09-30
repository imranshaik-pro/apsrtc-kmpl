"""Presentation-only helpers. Never change APSRTC values or history."""
import math
import re
from pathlib import Path

LOGO_URL = 'https://www.apsrtc.ap.gov.in/images/apsrtc_logo1.gif'
LOGO_PATH = Path(__file__).resolve().parent / 'assets' / 'apsrtc_logo.png'


def kmpl_number(value):
    if value is None or isinstance(value, bool):
        return None
    match = re.fullmatch(r'\s*([+-]?\d+(?:\.\d+)?)\s*(?:(?:🔧|⚙)[\s\d]*)?\s*', str(value))
    if not match:
        return None
    result = float(match.group(1))
    return result if math.isfinite(result) else None


def style_kmpl(cell):
    """Keep annotations and zeros intact; grade using existing KMPL bands."""
    from openpyxl.styles import PatternFill, Font
    value = kmpl_number(cell.value)
    if value is None:
        return
    bands = [(5, 'F4CCCC', '9C0006'), (5.1, 'FCE5CD', '7F6000'),
             (5.2, 'FFF2CC', '7F6000'), (5.3, 'D9EAD3', '274E13')]
    fill, text = next(((f, t) for limit, f, t in bands if value <= limit), ('B6D7A8', '274E13'))
    cell.fill = PatternFill('solid', fgColor=fill)
    cell.font = Font(name='Arial', size=10, color=text, bold=value <= 5 or value > 5.3)


def add_logo(ws, anchor='A1', width=180):
    from openpyxl.drawing.image import Image
    image = Image(str(LOGO_PATH))
    image.width = width
    image.height = width * 130 / 640
    ws.add_image(image, anchor)


def style_monthly_workbook(wb):
    for name, first_row, first_col, last_col in [('Monthly KMPL', 6, 5, None),
            ('Vehicle Performance', 6, 6, 17), ('Vehicle360', 5, 5, 5),
            ('Vehicle 360', 5, 5, 5)]:
        if name not in wb.sheetnames:
            continue
        ws = wb[name]
        add_logo(ws)
        for row in ws.iter_rows(min_row=first_row, min_col=first_col, max_col=last_col or ws.max_column):
            # History footer / exceptions are not vehicle performance records.
            if name == 'Vehicle Performance' and str(ws.cell(row[0].row, 5).value or '') not in {'2024-25', '2025-26', '2026-27'}:
                continue
            for cell in row:
                style_kmpl(cell)
