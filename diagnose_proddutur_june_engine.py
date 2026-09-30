"""Read-only Proddatur June engine source trace; no report publication."""
import json
import re
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup
from src.auth.client import login
import annual_kpi_runner_v3 as m

session=login()
period=m.token(2026,6)
params={'yymm':period,'reg':'YSRKADAPA','dept':'PRODDUTUR'}
seen=set()
def inspect(url, method='GET', data=None):
    key=(url,method,json.dumps(data or {},sort_keys=True))
    if key in seen: return []
    seen.add(key)
    try:
        response=session.post(url,data=data,timeout=30) if method=='POST' else session.get(url,timeout=30)
        print('SOURCE',method,url,'HTTP',response.status_code)
        if response.status_code!=200: return []
        soup=BeautifulSoup(response.text,'html.parser')
        heading=' '.join(soup.get_text(' ',strip=True).split())
        print('HEADING',heading[:300])
        if method=='POST':
            for table in soup.find_all('table'):
                rows=[m._expanded_dimension_cells(tr) for tr in table.find_all('tr')]
                if any('ENGINE' in ' '.join(r).upper() for r in rows):
                    print('ENGINE_TABLE',json.dumps(rows))
            print('PARSED',json.dumps(m.direct_dimension_rows(response.text,'ENGINE TYPE','ENGINE')))
        for form in soup.find_all('form'):
            print('FORM',form.get('method'),form.get('action'),
                  [(x.get('name'),x.get('value')) for x in form.find_all('input')],
                  [(x.get('name'),[(o.get('value'),o.get_text(' ',strip=True)) for o in x.find_all('option')][:8]) for x in form.find_all('select')])
        urls=[urljoin(url,a['href']) for a in soup.find_all('a',href=True)]
        urls += [urljoin(url,x) for x in re.findall(r"""['"]([^'"]*eng[^'"]*\.php)['"]""",response.text,re.I)]
        urls += [urljoin(url,x.get('src','')) for x in soup.find_all(['frame','iframe'])]
        relevant=[u for u in urls if urlsplit(u).hostname=='103.44.14.20' and any(k in u.lower() for k in ('eng','med','rindex'))]
        print('REPORT_LINKS',json.dumps(list(dict.fromkeys(relevant))))
        return relevant
    except Exception as exc:
        print('SOURCE_ERROR',type(exc).__name__,str(exc))
        return []



import io
import pdfplumber
url='http://103.44.14.20/med/booklet/jun-2026.pdf'
rr=session.get(url,timeout=45);rr.raise_for_status()
print('BOOKLET',url,'BYTES',len(rr.content))
with pdfplumber.open(io.BytesIO(rr.content)) as pdf:
    for index,page in enumerate(pdf.pages):
        text=page.extract_text() or ''
        if 'ENGINE' in text.upper() and ('PRODD' in text.upper() or any(k in text.upper() for k in ['EICHER-BS-III','NRE SPIN','1512TC'])):
            print('BOOKLET_ENGINE_PAGE',index+1,text)
            for table in page.extract_tables():
                if any('PRODD' in str(row).upper() for row in table):
                    print('BOOKLET_ENGINE_TABLE',index+1,json.dumps(table))
