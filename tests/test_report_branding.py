"""Offline presentation regressions; no report publication or source login."""
import unittest
from io import BytesIO
from zipfile import ZipFile
from openpyxl import Workbook, load_workbook
from report_branding import kmpl_number, style_monthly_workbook, LOGO_URL
from annual_visuals import dashboard_model, google_dashboard_requests, render_xlsx_dashboard


class BrandingTests(unittest.TestCase):
    def test_annotations_missing_and_zero(self):
        for value, expected in [('4.52 🔧 18', 4.52), ('5.31 ⚙', 5.31), (0, 0), ('—', None), ('MANUAL INPUT REQUIRED', None), ('', None), (True, None)]:
            self.assertEqual(kmpl_number(value), expected)

    def test_all_monthly_views_preserve_values_and_colour_annotations(self):
        w=Workbook(); w.remove(w.active)
        for name, row, col in [('Monthly KMPL',6,5),('Vehicle Performance',6,6),('Vehicle 360',5,5)]:
            s=w.create_sheet(name); s.cell(row,col,'4.52 🔧 18')
            s.cell(row+1,col,5.4); s.cell(row+2,col,0)
            if name=='Vehicle Performance':
                for r in range(row,row+3): s.cell(r,5,'2024-25')
        original={s.title:{c.coordinate:c.value for row in s for c in row if c.value is not None} for s in w}
        style_monthly_workbook(w)
        for s in w:
            self.assertEqual(original[s.title],{c.coordinate:c.value for row in s for c in row if c.value is not None})
            row,col=(5,5) if s.title=='Vehicle 360' else (6,6) if s.title=='Vehicle Performance' else (6,5)
            self.assertEqual(s.cell(row,col).fill.fgColor.rgb[-6:],'F4CCCC')
            self.assertEqual(s.cell(row+1,col).fill.fgColor.rgb[-6:],'B6D7A8')
            self.assertEqual(s.cell(row+2,col).fill.fgColor.rgb[-6:],'F4CCCC')
        b=BytesIO();w.save(b)
        self.assertEqual(len([p for p in ZipFile(b).namelist() if p.startswith('xl/media/')]),3)
        b.seek(0); saved=load_workbook(b)
        self.assertEqual(saved['Vehicle Performance']['F6'].value,'4.52 🔧 18')

    def test_annual_directions_missing_target_and_google_logo(self):
        fys=['2024-25','2025-26','2026-27']; rows=[]
        for name,target,value in [('TOTAL LUB KMPL',1600,1700),('B.D RATE',.03,.04),('MED CANCL.',.06,.06),('HSD KMPL INCL AC','',5.2)]:
            for fy in fys: rows.append([1,name,fy,target]+['']*13+[value])
        model=dashboard_model('PRODDUTUR',fys,rows,'2026-06')
        for name,fill in [('TOTAL LUB KMPL','E2F0D9'),('B.D RATE','F4CCCC'),('MED CANCL.','E2F0D9'),('HSD KMPL INCL AC','FFF2D9')]:
            r=next(c['r'] for c in model['cells'] if c['text']==name)
            self.assertEqual(next(c['fill'] for c in model['cells'] if c['r']==r and c['c']==6),fill)
        requests=google_dashboard_requests(12,model)
        self.assertIn(LOGO_URL,str(requests));self.assertIn('formulaValue',str(requests))
        w=Workbook();render_xlsx_dashboard(w,'Dashboard',model,'PRODDUTUR','2026-06')
        b=BytesIO();w.save(b)
        self.assertTrue(any(p.startswith('xl/media/') for p in ZipFile(b).namelist()))

if __name__=='__main__': unittest.main()
