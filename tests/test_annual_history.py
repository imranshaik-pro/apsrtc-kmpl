"""Regression tests for durable history, source call counts and view selection."""
import ast
import copy
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import annual_history as h
import telegram_command_bot as bot

class Model:
    @staticmethod
    def new_store(fys): return {'fys':fys,'order':[],'rows':{}}
    @staticmethod
    def ensure(st,name):
        if name not in st['rows']:
            st['order'].append(name)
            st['rows'][name]={fy:{'months':{},'upto':None} for fy in st['fys']}
    @classmethod
    def seed(cls,st):
        for names in h.GROUPS.values():
            for name in names: cls.ensure(st,name)
    @staticmethod
    def valid_dynamic(name): return True

def source(group,period):
    names=h.GROUPS[group] or [group+': TATA']
    mo=int(period[-2:])
    return {name:{'month':mo,'upto':mo+100} for name in names}

class HistoryTests(unittest.TestCase):
    def setUp(self): self.cache=h.new_cache('RAJAMPET')

    def test_june_august_june_and_repeat_have_no_historical_fetches(self):
        fetch=Mock(side_effect=source)
        h.update(self.cache,['2026-27'],'2026-06',fetch)
        self.assertEqual(fetch.call_count,24)
        fetch.reset_mock()
        h.update(self.cache,['2026-27'],'2026-06',fetch)
        fetch.assert_not_called()
        h.update(self.cache,['2026-27'],'2026-08',fetch)
        self.assertEqual(fetch.call_count,16)
        self.assertEqual({c.args[1] for c in fetch.call_args_list},{'2026-07','2026-08'})
        before=copy.deepcopy(self.cache)
        fetch.reset_mock(); h.update(self.cache,['2026-27'],'2026-06',fetch)
        fetch.assert_not_called()
        view=h.view_store(self.cache,['2026-27'],'2026-06',Model)
        row=view['rows']['HSD KMPL INCL AC']['2026-27']
        self.assertEqual(row['upto'],106)
        self.assertNotIn('Jul',row['months'])
        self.assertEqual(self.cache,before)
        self.assertEqual(self.cache['months']['2026-08']['HSD']['HSD KMPL INCL AC']['upto'],108)

    def test_completed_fy_reused_and_rollover_keeps_old_fy(self):
        h.update(self.cache,['2025-26'],'2026-03',source)
        fetch=Mock(side_effect=source)
        h.update(self.cache,['2025-26','2026-27'],'2026-04',fetch)
        self.assertEqual(fetch.call_count,8)
        self.assertEqual({c.args[1] for c in fetch.call_args_list},{'2026-04'})
        view=h.view_store(self.cache,['2025-26','2026-27'],'2026-04',Model)
        self.assertEqual(view['rows']['HSD KMPL INCL AC']['2025-26']['upto'],103)

    def test_source_failure_and_blank_cannot_erase_saved_zero(self):
        h.update(self.cache,['2026-27'],'2026-06',source)
        item=self.cache['months']['2026-06']['HSD']['HSD KMPL INCL AC']
        item['month']=0; del item['upto']
        old=copy.deepcopy(self.cache)
        fetch=Mock(side_effect=TimeoutError('offline'))
        h.update(self.cache,['2026-27'],'2026-06',fetch)
        self.assertEqual(fetch.call_count,1); self.assertEqual(self.cache,old)
        h.update(self.cache,['2026-27'],'2026-06',lambda *_:{'HSD KMPL INCL AC':{'month':None,'upto':h.MANUAL}})
        self.assertEqual(self.cache,old)

    def test_existing_workbook_migration_with_no_meta_and_ragged_rows(self):
        values=[['APSRTC RAJAMPET'],['ANNUAL KPI — Through June 2026'],[],[],
                ['SL.No','KPI','Year','Target'],
                [1,'HSD KMPL INCL AC','2025-26',5]+list(range(12))+['',5.4],
                ['','','2026-27',5,0,5.1,5.2]+['']*10+[5.3]]
        h.migrate(self.cache,values,h.period_from_heading(values))
        self.assertEqual(self.cache['months']['2026-03']['HSD']['HSD KMPL INCL AC']['upto'],5.4)
        self.assertEqual(self.cache['months']['2026-06']['HSD']['HSD KMPL INCL AC']['upto'],5.3)
        self.assertEqual(self.cache['months']['2026-04']['HSD']['HSD KMPL INCL AC']['month'],0)
        self.assertEqual(self.cache['legacy'],values)

    def test_unknown_legacy_upto_never_assigned_to_requested_month(self):
        h.migrate(self.cache,[['SL.No','KPI','Year','Target'],[1,'HSD KMPL INCL AC','2026-27','',5]+['']*12+[99]])
        self.assertNotIn('upto',self.cache['months']['2026-04']['HSD']['HSD KMPL INCL AC'])

    def test_persistence_roundtrip_and_corruption_fail_closed(self):
        self.cache['legacy']=[['x'*32000]]
        rows=h.encode(self.cache)
        self.assertGreater(len(rows),2)
        self.assertEqual(h.decode(rows+[['stale trailing data']],'RAJAMPET'),self.cache)
        for broken in (rows[:-1],[[h.SCHEMA,'OTHER',1,'bad']],[]):
            with self.assertRaises(ValueError): h.decode(broken,'RAJAMPET')

    def test_known_fy24_unavailable_sources_not_requested(self):
        fetch=Mock(side_effect=source)
        h.update(self.cache,['2024-25'],'2025-03',fetch)
        self.assertFalse(any(c.args[0] in ('LUB','SPRING') for c in fetch.call_args_list))
        self.assertEqual([c.args[1] for c in fetch.call_args_list if c.args[0]=='TYRE'],['2024-04'])
        self.assertEqual(self.cache['months']['2025-03']['TYRE']['AVG TYRE LIFE']['month'],h.MANUAL)

    def test_cache_save_failure_stops_processing(self):
        with self.assertRaises(OSError):
            h.update(self.cache,['2026-27'],'2026-06',source,Mock(side_effect=OSError('write failed')))
        self.assertNotIn('2026-05',self.cache['months'])

    def test_finalizer_never_deletes_cache_or_other_sheets(self):
        tree=ast.parse((ROOT/'annual_kpi_runner_v11.py').read_text())
        fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_finalize_live_workbook')
        svc=Mock(); svc.spreadsheets.return_value=svc
        svc.get.return_value.execute.return_value={'sheets':[{'properties':{'sheetId':i,'title':t}} for i,t in enumerate(['Annual KPI','Dashboard',h.CACHE_TITLE,'_META','Legacy'])]}
        env={'m':types.SimpleNamespace(sheets_service=lambda:svc,SHEET_TITLE='Annual KPI'),'DASHBOARD_TITLE':'Dashboard','DETAIL_TITLE':'Detail'}
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'<finalizer>','exec'),env)
        env['_finalize_live_workbook']('same-id')
        req=svc.batchUpdate.call_args.kwargs['body']['requests']
        self.assertFalse(any('deleteSheet' in r for r in req))
        self.assertEqual({r['updateSheetProperties']['properties']['sheetId'] for r in req if r['updateSheetProperties']['properties'].get('hidden')},{2,3,4})

    def test_depot_first_telegram_flow(self):
        with patch.object(bot,'DEPOTS',('RAJAMPET',)),patch.object(bot,'send') as send,patch.object(bot,'answer_callback'):
            bot.handle_message('t','c','/menu')
            self.assertEqual(send.call_args.args[3][0][0]['callback_data'],'depot|RAJAMPET')
            bot.handle_callback('t','c',{'data':'depot|RAJAMPET'})
            buttons=[b['callback_data'] for row in send.call_args.args[3] for b in row]
            self.assertIn('annual|RAJAMPET',buttons); self.assertIn('event|RAJAMPET',buttons)

    def test_runner_reuses_same_sheet_and_never_calls_legacy_rebuild(self):
        from datetime import datetime
        import os
        fys=['2024-25','2025-26','2026-27']
        h.update(self.cache,fys,'2026-06',source)
        self.cache['target_attempts']=fys[:]
        saved={'cache':h.encode(self.cache)}
        svc=Mock(); svc.spreadsheets.return_value=svc
        svc.get.return_value.execute.return_value={'sheets':[{'properties':{'title':h.CACHE_TITLE}}]}
        def write(sid,rng,rows):
            self.assertEqual(sid,'existing-depot-id')
            if h.CACHE_TITLE in rng: saved['cache']=rows
        fetch=Mock(side_effect=lambda s,d,v,r,y,mo:source('HSD',f'{y}-{mo:02}'))
        model=types.SimpleNamespace(
            core=types.SimpleNamespace(depot_info=lambda d:('RJP','RAJAMPET','KADAPA'),DEFAULT_DRIVE_FOLDER='folder'),
            fy_triplet=lambda *_:fys,find_file=lambda *_:{'id':'existing-depot-id'},
            sheets_service=lambda:svc,read_values=lambda *_:saved['cache'],write_values=write,
            ensure_hidden_sheet=lambda *_:99,META_TITLE='_META',login=Mock(),
            new_store=Model.new_store,seed=Model.seed,ensure=Model.ensure,valid_dynamic=Model.valid_dynamic,
            fetch_hsd=fetch,fetch_lub=Mock(),fetch_bd=Mock(),fetch_med=Mock(),fetch_spring=Mock())
        tree=ast.parse((ROOT/'annual_kpi_runner_v11.py').read_text())
        fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main_v11')
        formatter=Mock(); old_main=Mock(side_effect=AssertionError('Legacy rebuild must never run'))
        env=dict(history=h,datetime=datetime,os=os,sys=types.SimpleNamespace(argv=['run','--depot','RAJAMPET','--selected-month','2026-06']),
            m=model,v7=types.SimpleNamespace(matrix_with_target=lambda st:st),v10=Mock(),LAYOUT_VERSION='10',
            ORIGINAL_V7_MAIN=old_main,DETAIL_TITLE='Detail',make_xlsx_v11=Mock(),format_sheet_v11=formatter,
            _style_live_detail=Mock(),_ensure_dashboard_google_sheet=Mock(),_add_live_identity=Mock(),_finalize_live_workbook=Mock())
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'<runner>','exec'),env)
        self.assertEqual(env['main_v11'](),0)
        model.login.assert_not_called(); old_main.assert_not_called()
        self.assertEqual(formatter.call_args.args[0],'existing-depot-id')
        self.assertEqual(h.decode(saved['cache'],'RAJAMPET')['months'],self.cache['months'])

if __name__=='__main__': unittest.main()
