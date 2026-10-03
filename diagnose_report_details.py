"""Read-only source evidence for the new report tabs; no Drive or Telegram writes."""
import argparse
import json
import re
from calendar import monthrange
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup
from src.auth.client import login
from annual_kpi_report import depot_info


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--depot', required=True)
    parser.add_argument('--months', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    _, display, region = depot_info(args.depot)
    session = login()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    result = []
    for period in args.months.split(','):
        dt = datetime.strptime(period, '%Y-%m')
        last = monthrange(dt.year, dt.month)[1]
        for mode in ('UD', 'UM'):
            payload = {'fdate': f'{last}/{dt.month}/{dt.year}', 'reg': region,
                       'dept': display, 'fupto': mode}
            response = session.post('http://103.44.14.20/mednew/eng_prod_um.php',
                                    data=payload, timeout=45)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            tables = [table for table in soup.find_all('table')
                      if re.search(r'ENGINE\s+MODEL', table.get_text(' ', strip=True), re.I)]
            if len(tables) != 1:
                raise RuntimeError(f'{display} {period} {mode}: expected one engine/product table')
            headings = [x.get_text(' ', strip=True) for x in soup.find_all(re.compile('^h[1-6]$'))]
            rows = [[cell.get_text(' ', strip=True) for cell in row.find_all(['th', 'td'], recursive=False)]
                    for row in tables[0].find_all('tr')]
            record = {'depot': display, 'period': period, 'mode': mode, 'request': payload,
                      'headings': headings, 'rows': rows}
            result.append(record)
            (out / f'{period}-{mode}.html').write_text(
                '\n'.join(str(x) for x in soup.find_all(re.compile('^h[1-6]$'))) + '\n' + str(tables[0]),
                encoding='utf-8')
            print(json.dumps(record, ensure_ascii=False))
    (out / 'source-contracts.json').write_text(json.dumps(result, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
