"""Offline presentation and value-screening contracts; no live services."""
import copy
import json
import math
import unittest
from unittest.mock import patch

import annual_visuals as v
from annual_value_audit import ratio_reviews, count_sum

FYS=['2024-25','2025-26','2026-27']


def matrix(name='HSD KMPL INCL AC', value=4.99, target=5.03):
    return [[1,name,'2026-27',target,5.05,4.94]+['']*10+['',value]]


class AnnualDashboardTests(unittest.TestCase):
    def test_source_targets_and_lower_better_rules(self):
        self.assertEqual(v.target_status('HSD KMPL INCL AC',4.99,5.03)[0],'BELOW TARGET')
        self.assertEqual(v.target_status('TOTAL LUB KMPL',1829,1800)[0],'ON TARGET')
        self.assertEqual(v.target_status('B.D RATE',.0443,.04)[0],'BELOW TARGET')
        self.assertEqual(v.target_status('MED CANCL.',0,.01)[0],'ON TARGET')
        self.assertEqual(v.target_status('PRODUCT: EXPRESS',5,None)[0],'NO TARGET')
        self.assertEqual(v.target_status('HSD KMPL INCL AC',None,5)[0],'UNAVAILABLE')
        self.assertEqual(v.target_status('AVG TYRE LIFE',2.03,2.1)[0],'NO TARGET')

    def test_formats_units_and_round_half_up(self):
        self.assertEqual(v.kpi_format('B.D RATE'),'0.0000')
        self.assertEqual(v.kpi_format('TOTAL LUB KMPL'),'0.00')
        self.assertEqual(v.target_delta('B.D RATE',.0443,.04),'+0.0043 vs target 0.0400')
        self.assertEqual(v.target_delta('HSD KMPL INCL AC',5.005,5),'+0.01 vs target 5.00')

    def test_no_nan_and_real_zero(self):
        for value in ('—','MANUAL INPUT REQUIRED',float('nan'),float('inf'),True):
            self.assertIsNone(v.number(value))
        self.assertEqual(v.number(0),0)
        self.assertIsNone(count_sum(None,0))
        self.assertEqual(count_sum(0,0),0)

    def test_named_anchors_preserve_input_and_source_precision(self):
        rows=matrix('B.D RATE',.0443,.04); old=copy.deepcopy(rows)
        m=v.dashboard_model('PRODDUTUR',FYS,rows,'2026-05')
        self.assertEqual(rows,old)
        card=next(a for a in m['anchors']['hero'] if a['kpi']=='B.D RATE')
        value=next(c for c in m['cells'] if [c['r'],c['c']]==card['value'])
        self.assertEqual(value['text'],.0443);self.assertEqual(value['fmt'],'0.0000')
        self.assertEqual(json.dumps(m,sort_keys=True),json.dumps(v.dashboard_model('PRODDUTUR',FYS,rows,'2026-05'),sort_keys=True))

    def test_month_cutoff_target_series_and_missing_engine_details(self):
        for month,count in [('2026-04',1),('2026-05',2),('2026-07',4),('2027-03',12)]:
            m=v.dashboard_model('PRODDUTUR',FYS,matrix(),month)
            self.assertEqual([s['points'] for s in m['charts']],[count,count])
            self.assertEqual(m['charts'][0]['labels'],['Incl. AC','Excl. AC','Incl. AC target'])
        rows=matrix('ENGINE: Exact historical label',None,None)
        m=v.dashboard_model('PRODDUTUR',FYS,rows,'2026-05')
        self.assertNotIn('ENGINE: Exact historical label',m['anchors']['summary'])
        self.assertTrue(any('1 engine rows' in str(c['text']) for c in m['cells']))
        self.assertEqual(rows[0][1],'ENGINE: Exact historical label')

    def test_google_matches_formats_and_target_cells(self):
        m=v.dashboard_model('PRODDUTUR',FYS,matrix('B.D RATE',.0443,.04),'2026-05')
        req=v.google_dashboard_requests(12,m)
        self.assertEqual(sum('addChart' in r for r in req),2)
        self.assertTrue(any(r.get('repeatCell',{}).get('cell',{}).get('userEnteredFormat',{}).get('numberFormat',{}).get('pattern')=='0.0000' for r in req))

    def test_xlsx_renderer_uses_model_geometry_and_keeps_other_sheets(self):
        from openpyxl import Workbook
        wb=Workbook();wb.active.title='Detailed';wb.active['A1']='saved'
        m=v.dashboard_model('PRODDUTUR',FYS,matrix(),'2026-05')
        with patch.object(v,'add_logo'):
            ws=v.render_xlsx_dashboard(wb,'Dashboard',m,'PRODDUTUR','2026-05')
        self.assertEqual(wb['Detailed']['A1'].value,'saved')
        self.assertEqual(len(ws._charts[0].series),3)
        self.assertEqual(ws._charts[0].series[-1].graphicalProperties.line.prstDash,'dash')
        self.assertEqual(ws.page_setup.fitToWidth,1)
        self.assertEqual(ws.page_setup.fitToHeight,1)
        self.assertTrue(ws.column_dimensions['X'].hidden)

    def test_reconciliation_sparse_months_are_unverified_and_inputs_unchanged(self):
        rows=matrix(value=5.3);before=copy.deepcopy(rows)
        reviews=ratio_reviews(rows,FYS,'2026-05')
        self.assertEqual(reviews[0]['severity'],'review')
        rows[0][4]=''
        self.assertEqual(ratio_reviews(rows,FYS,'2026-05')[0]['severity'],'unverified')
        self.assertEqual(before[0][17],5.3)

    def test_rounding_boundary_is_not_a_false_range_warning(self):
        self.assertEqual(ratio_reviews(matrix(value=5.06),FYS,'2026-05'),[])

    def test_may_july_may_changes_only_visible_months_and_retains_cached_history(self):
        import annual_history as h
        from unittest.mock import Mock
        cache=h.new_cache('PRODDUTUR')
        def fetched(group,period):
            names=h.GROUPS[group] or [group+': Exact source label']
            return {name:{'month':int(period[-2:]),'upto':100+int(period[-2:])} for name in names}
        fetch=Mock(side_effect=fetched)
        h.update(cache,['2026-27'],'2026-05',fetch)
        before=copy.deepcopy(cache['months']);fetch.reset_mock()
        h.update(cache,['2026-27'],'2026-07',fetch)
        self.assertEqual({c.args[1] for c in fetch.call_args_list},{'2026-06','2026-07'})
        for period in ('2026-04','2026-05'):self.assertEqual(cache['months'][period],before[period])
        saved=copy.deepcopy(cache);fetch.reset_mock()
        h.update(cache,['2026-27'],'2026-05',fetch)
        fetch.assert_not_called();self.assertEqual(cache,saved)
        # The current presentation always stops at the selected month.
        may=v.dashboard_model('PRODDUTUR',FYS,matrix(),'2026-05')
        july=v.dashboard_model('PRODDUTUR',FYS,matrix(),'2026-07')
        again=v.dashboard_model('PRODDUTUR',FYS,matrix(),'2026-05')
        self.assertEqual(may,again)
        self.assertEqual([may['charts'][0]['points'],july['charts'][0]['points']],[2,4])


if __name__=='__main__': unittest.main()
