"""Read-only observed range source forms; no delivery or external writes."""
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from src.auth.client import login
s=login();out=Path('reports/depot-range-source');out.mkdir(parents=True,exist_ok=True)
for path in ['vehlog_kmpl1.php','drvlog_kmpl1.php','vehlog_ckmpl.php','drvlog_ckmpl.php']:
 r=s.get('http://103.44.14.20/med/'+path,timeout=45);r.raise_for_status()
 soup=BeautifulSoup(r.text,'html.parser')
 print('SOURCE_FORM',path,[(f.get('action'),f.get('method'),[(i.get('name'),i.get('value')) for i in f.find_all(['input','select'])]) for f in soup.find_all('form')])
 if path.endswith('kmpl1.php'):
  f=soup.find('form');r=s.post(urljoin(r.url,f['action']),data={'yymm':'202609'},timeout=45);r.raise_for_status()
 else:
  r=s.post(r.url,data={'yymm':'202609'},timeout=45);r.raise_for_status()
 soup=BeautifulSoup(r.text,'html.parser');(out/path).write_text(r.text)
 print('SOURCE_PARENT',path,[h.get_text(' ',strip=True) for h in soup.find_all(['h2','h3'])],[(a.get_text(' ',strip=True),a['href']) for a in soup.find_all('a',href=True) if 'YSR' in a.get_text() or 'YSR' in a['href']])
 for a in soup.find_all('a',href=True):
  if 'YSR' in a.get_text() or 'YSR' in a['href']:
   rr=s.get(urljoin(r.url,a['href']),timeout=45);rr.raise_for_status();ss=BeautifulSoup(rr.text,'html.parser');(out/(path+'-depot.html')).write_text(rr.text)
   print('SOURCE_DEPOT',rr.url,[h.get_text(' ',strip=True) for h in ss.find_all(['h2','h3'])],[[c.get_text(' ',strip=True) for c in tr.find_all(['th','td'],recursive=False)] for tr in ss.find_all('tr') if 'PRODDUTUR' in tr.get_text() or 'RAJAMPET' in tr.get_text()])
