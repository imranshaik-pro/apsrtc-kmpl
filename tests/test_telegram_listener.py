import os
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import Mock, patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import telegram_listener as listener
import telegram_command_bot as bot

class ListenerTests(unittest.TestCase):
    def test_restart_does_not_replay_completed_request(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'state.sqlite3'; db=listener.open_state(p); fn=Mock()
            self.assertEqual(listener.process(db,{'update_id':42},fn),'done')
            db.close(); db=listener.open_state(p)
            self.assertEqual(listener.process(db,{'update_id':42},fn),'duplicate')
            fn.assert_called_once(); db.close()

    def test_ambiguous_failure_is_recorded_without_automatic_replay(self):
        db=listener.open_state(':memory:'); fn=Mock(side_effect=TimeoutError())
        with self.assertRaises(TimeoutError): listener.process(db,{'update_id':7},fn)
        self.assertEqual(listener.process(db,{'update_id':7},fn),'duplicate')
        self.assertEqual(db.execute('SELECT status FROM updates').fetchone()[0],'failed')
        fn.assert_called_once(); db.close()

    def test_poll_http_timeout_exceeds_telegram_timeout(self):
        with patch.object(bot,'_request',return_value={'ok':True,'result':[]}) as req:
            bot.telegram('test','getUpdates',{'timeout':20})
        self.assertEqual(req.call_args.kwargs['timeout'],35)

    def test_dates_show_depot_and_reject_today_or_future_daily(self):
        with patch.object(bot,'DEPOTS',('RAJAMPET',)),patch.object(bot,'today_ist',return_value=date(2026,9,24)),patch.object(bot,'send') as send,patch.object(bot,'answer_callback'),patch.object(bot,'dispatch') as dispatch:
            bot.handle_callback('t','c',{'data':'daily|RAJAMPET'})
            self.assertIn('RAJAMPET',send.call_args.args[2])
            self.assertEqual(send.call_args.args[3][0][0]['callback_data'],'dailyrun|RAJAMPET|2026-09-23')
            bot.handle_callback('t','c',{'data':'dailyrun|RAJAMPET|2026-09-23'})
            dispatch.assert_called_once_with('daily-report.yml',{'depot':'RAJAMPET','report_date':'2026-09-23'})
            dispatch.reset_mock()
            bot.handle_callback('t','c',{'data':'dailyrun|RAJAMPET|2026-09-24'})
            dispatch.assert_not_called()

    def test_process_payload_does_not_refetch_queue(self):
        with patch.dict(os.environ,{'TELEGRAM_BOT_TOKEN':'test','TELEGRAM_CHAT_ID':'123'}),patch.object(bot,'telegram') as api,patch.object(bot,'handle_message') as handler:
            bot.main({'ok':True,'result':[{'update_id':1,'message':{'chat':{'id':123},'text':'/menu'}}]})
            handler.assert_called_once_with('test','123','/menu')
            self.assertEqual(api.call_count,1)
            self.assertEqual(api.call_args.args[2]['offset'],2)

if __name__=='__main__': unittest.main()
