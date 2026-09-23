import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import telegram_command_bot as bot

class ConfigurationTests(unittest.TestCase):
    def test_registration_scope_and_readback_without_messages(self):
        calls=[]
        def api(token,method,params):
            calls.append((method,params))
            return {'ok':True,'result':bot.BOT_COMMANDS if method=='getMyCommands' else True}
        with patch.object(bot,'telegram',side_effect=api): bot.configure_commands('test','123')
        self.assertEqual([m for m,_ in calls],['setMyCommands','getMyCommands','setMyCommands','getMyCommands','setChatMenuButton'])
        self.assertEqual(json.loads(calls[0][1]['scope']),{'type':'chat','chat_id':'123'})

    def test_failed_readback_is_not_reported_as_success(self):
        def api(token,method,params):
            return {'ok':True,'result':[] if method=='getMyCommands' else True}
        with patch.object(bot,'telegram',side_effect=api):
            with self.assertRaises(RuntimeError): bot.configure_commands('test','123')

    def test_group_chat_has_no_private_menu_call(self):
        with patch.object(bot,'telegram',side_effect=lambda t,m,p:{'ok':True,'result':bot.BOT_COMMANDS if m=='getMyCommands' else True}) as api:
            bot.configure_commands('test','-100123')
        self.assertNotIn('setChatMenuButton',[c.args[1] for c in api.call_args_list])

if __name__=='__main__': unittest.main()
