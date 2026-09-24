"""Always-on long polling. Run one instance, with durable local update claims."""
import fcntl
import json
import os
from pathlib import Path
import sqlite3
import time
from urllib.error import HTTPError, URLError

import telegram_command_bot as bot

def open_state(path):
    db=sqlite3.connect(path)
    db.execute('PRAGMA synchronous=FULL')
    db.execute('CREATE TABLE IF NOT EXISTS updates (id INTEGER PRIMARY KEY, status TEXT NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS identity (id INTEGER PRIMARY KEY CHECK(id=1), bot_id TEXT NOT NULL)')
    db.commit()
    return db

def process(db, update, handler):
    uid=int(update['update_id'])
    # Reserve before side effects. A crash/ambiguous HTTP error must not dispatch
    # another report or submit a vehicle event automatically on restart.
    with db:
        claim=db.execute('INSERT OR IGNORE INTO updates VALUES (?,?)',(uid,'claimed'))
    if not claim.rowcount: return 'duplicate'
    try:
        handler({'ok':True,'result':[update]})
    except Exception:
        with db: db.execute('UPDATE updates SET status=? WHERE id=?',('failed',uid))
        raise
    with db: db.execute('UPDATE updates SET status=? WHERE id=?',('done',uid))
    return 'done'

def serve():
    required=('TELEGRAM_BOT_TOKEN','TELEGRAM_CHAT_ID','GH_DISPATCH_TOKEN','DEPOT_MASTER',
              'VEHICLE_EVENTS_API_URL','VEHICLE_EVENTS_API_KEY')
    missing=[key for key in required if not os.getenv(key,'').strip()]
    if missing: raise RuntimeError('Missing configuration: '+', '.join(missing))
    root=Path(os.environ.get('TELEGRAM_STATE_DIR','/var/lib/apsrtc-telegram'))
    root.mkdir(parents=True,exist_ok=True)
    lock=(root/'listener.lock').open('a')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    token=os.environ['TELEGRAM_BOT_TOKEN'].strip()
    if bot.telegram(token,'getWebhookInfo',{})['result'].get('url'):
        raise RuntimeError('A Telegram webhook is active; remove it before using this listener')
    identity=str(bot.telegram(token,'getMe',{})['result']['id'])
    db=open_state(root/'updates.sqlite3')
    old=db.execute('SELECT bot_id FROM identity WHERE id=1').fetchone()
    if old and old[0]!=identity: raise RuntimeError('State belongs to another bot')
    with db: db.execute('INSERT OR IGNORE INTO identity VALUES (1,?)',(identity,))
    bot.configure_commands(token,os.environ['TELEGRAM_CHAT_ID'].strip())
    last=db.execute('SELECT MAX(id) FROM updates').fetchone()[0]
    offset=last+1 if last is not None else 0
    delay=1
    print('TELEGRAM_LISTENER_READY: continuous long polling',flush=True)
    while True:
        try:
            payload=bot.telegram(token,'getUpdates',{'offset':offset,'timeout':20,'limit':100,
                'allowed_updates':json.dumps(['message','callback_query'])})
            delay=1
        except HTTPError as exc:
            if exc.code in (401,403,409):
                raise RuntimeError('Telegram authentication or competing-listener error') from None
            print(f'TELEGRAM_POLL_RETRY: HTTP {exc.code}',flush=True)
            time.sleep(delay); delay=min(30,delay*2); continue
        except (URLError,TimeoutError):
            print('TELEGRAM_POLL_RETRY: network error',flush=True)
            time.sleep(delay); delay=min(30,delay*2); continue
        for update in payload.get('result',[]):
            uid=int(update['update_id'])
            try:
                result=process(db,update,bot.main)
                print(f'TELEGRAM_UPDATE: {uid} {result}',flush=True)
            except Exception as exc:
                # Do not log token-bearing URLs or event payloads.
                print(f'TELEGRAM_UPDATE_FAILED: {uid} {type(exc).__name__}; no automatic replay',flush=True)
                msg=update.get('message') or (update.get('callback_query') or {}).get('message') or {}
                authorized=os.environ['TELEGRAM_CHAT_ID'].strip()
                if str((msg.get('chat') or {}).get('id',''))==authorized:
                    try: bot.send(token,authorized,'This request could not be confirmed. Check the report run or event ID before resubmitting; it will not be retried automatically.')
                    except Exception: pass
            offset=max(offset,uid+1)

if __name__=='__main__': serve()
