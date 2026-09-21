"""Authorized Telegram menu/command processor for APSRTC automation."""
from __future__ import annotations
import json, os, re, urllib.parse, urllib.request
from datetime import date, datetime

API="https://api.telegram.org/bot{token}/{method}"
REPO=os.getenv("GITHUB_REPOSITORY","imranshaik-pro/apsrtc-kmpl")
REF=os.getenv("GITHUB_REF_NAME","master")
# Keep this list aligned with the operational depot choices used by the Forms.
DEPOTS=("PRODDUTUR","KADAPA","BADVEL")

def _request(url, *, data=None, headers=None):
    req=urllib.request.Request(url,data=data,headers=headers or {})
    with urllib.request.urlopen(req,timeout=25) as r: return json.load(r)

def telegram(token,method,params):
    return _request(API.format(token=token,method=method),data=urllib.parse.urlencode(params).encode())

def send(token,chat_id,text,keyboard=None):
    p={"chat_id":chat_id,"text":text,"disable_web_page_preview":"true"}
    if keyboard: p["reply_markup"]=json.dumps({"inline_keyboard":keyboard})
    return telegram(token,"sendMessage",p)

def answer_callback(token,callback_id,text=""):
    telegram(token,"answerCallbackQuery",{"callback_query_id":callback_id,"text":text})

def dispatch(workflow,inputs):
    gh=os.environ["GH_DISPATCH_TOKEN"].strip()
    body=json.dumps({"ref":REF,"inputs":inputs}).encode()
    req=urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/actions/workflows/{workflow}/dispatches",
        data=body,method="POST",
        headers={"Authorization":f"Bearer {gh}","Accept":"application/vnd.github+json",
                 "X-GitHub-Api-Version":"2022-11-28","Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=25) as r:
        if r.status!=204: raise RuntimeError(f"GitHub dispatch returned HTTP {r.status}")

def depot_keyboard(action):
    return [[{"text":d,"callback_data":f"{action}|{d}"}] for d in DEPOTS]

def month_keyboard(depot):
    today=date.today()
    months=[]
    y,m=today.year,today.month
    for _ in range(6):
        value=f"{y:04d}-{m:02d}"
        months.append([{"text":value,"callback_data":f"monthlyrun|{depot}|{value}"}])
        m-=1
        if m==0: m=12;y-=1
    return months

def main_menu():
    return [
        [{"text":"📅 Daily Report","callback_data":"menu|daily"},
         {"text":"📊 Monthly Report","callback_data":"menu|monthly"}],
        [{"text":"🚌 Vehicle 360","callback_data":"menu|vehicle"},
         {"text":"🛠 Vehicle Event","callback_data":"menu|event"}],
        [{"text":"✅ Status","callback_data":"menu|status"}],
    ]

def help_text():
    return ("🚌 APSRTC AUTOMATION BOT\n\nChoose an action below. "
            "Daily and Monthly reports will ask for the depot before anything is triggered.")

def handle_message(token,chat_id,text):
    parts=text.strip().split()
    cmd=parts[0].split("@",1)[0].lower() if parts else ""
    if cmd in ("/start","/help","/menu"):
        send(token,chat_id,help_text(),main_menu()); return
    if cmd=="/status":
        send(token,chat_id,"✅ APSRTC automation bot is online.\nAuthorized chat verified.",main_menu()); return
    if cmd=="/daily":
        send(token,chat_id,"Select depot for Daily Report:",depot_keyboard("daily")); return
    if cmd=="/monthly":
        send(token,chat_id,"Select depot for Monthly Report:",depot_keyboard("monthly")); return
    if cmd=="/vehicle":
        send(token,chat_id,"Vehicle 360 lookup is the next phase. No report has been triggered.",main_menu()); return
    if cmd=="/event":
        send(token,chat_id,"Vehicle Event guided entry is the next phase. No event has been written.",main_menu()); return
    send(token,chat_id,"Use /menu to open the APSRTC menu.",main_menu())

def handle_callback(token,chat_id,cq):
    data=str(cq.get("data") or "")
    cid=str(cq.get("id") or "")
    answer_callback(token,cid)
    parts=data.split("|")
    if data=="menu|daily":
        send(token,chat_id,"Select depot for Daily Report:",depot_keyboard("daily")); return
    if data=="menu|monthly":
        send(token,chat_id,"Select depot for Monthly Report:",depot_keyboard("monthly")); return
    if data=="menu|status":
        send(token,chat_id,"✅ APSRTC automation bot is online.\nAuthorized chat verified.",main_menu()); return
    if data=="menu|vehicle":
        send(token,chat_id,"🚌 Vehicle 360 lookup is the next phase. No report triggered.",main_menu()); return
    if data=="menu|event":
        send(token,chat_id,"🛠 Vehicle Event guided entry is the next phase. No event written.",main_menu()); return
    if len(parts)==2 and parts[0]=="daily" and parts[1] in DEPOTS:
        depot=parts[1]
        keyboard=[
          [{"text":"▶ Latest completed day","callback_data":f"dailyrun|{depot}|latest"}],
          [{"text":"⬅ Back to depots","callback_data":"menu|daily"}],
        ]
        send(token,chat_id,f"Daily Report — {depot}\nChoose report date:",keyboard); return
    if len(parts)==3 and parts[0]=="dailyrun" and parts[1] in DEPOTS and parts[2]=="latest":
        depot=parts[1]
        dispatch("daily-report.yml",{"depot":depot,"report_date":""})
        send(token,chat_id,f"⏳ Daily report requested for {depot}.\nThe existing workflow will deliver it here when complete.",main_menu()); return
    if len(parts)==2 and parts[0]=="monthly" and parts[1] in DEPOTS:
        send(token,chat_id,f"Monthly Report — {parts[1]}\nSelect month:",month_keyboard(parts[1])); return
    if len(parts)==3 and parts[0]=="monthlyrun" and parts[1] in DEPOTS:
        depot,month=parts[1],parts[2]
        try: datetime.strptime(month,"%Y-%m")
        except ValueError:
            send(token,chat_id,"Invalid month.",main_menu()); return
        if month>date.today().strftime("%Y-%m"):
            send(token,chat_id,"Future months are not allowed.",main_menu()); return
        dispatch("monthly-report.yml",{"depot":depot,"month":month})
        send(token,chat_id,f"⏳ Monthly report requested for {depot} — {month}.",main_menu()); return
    send(token,chat_id,"That menu option is no longer valid. Open /menu again.",main_menu())

def main():
    token=os.environ["TELEGRAM_BOT_TOKEN"].strip()
    authorized=os.environ["TELEGRAM_CHAT_ID"].strip()
    payload=telegram(token,"getUpdates",{
        "timeout":0,"limit":100,
        "allowed_updates":json.dumps(["message","callback_query"])})
    updates=payload.get("result",[])
    max_update=0
    for update in updates:
        uid=int(update.get("update_id",0)); max_update=max(max_update,uid+1)
        cq=update.get("callback_query")
        if cq:
            msg=cq.get("message") or {}
            incoming=str((msg.get("chat") or {}).get("id",""))
            if incoming==authorized: handle_callback(token,authorized,cq)
            elif incoming: answer_callback(token,str(cq.get("id") or ""),"Unauthorized")
            continue
        msg=update.get("message") or {}
        incoming=str((msg.get("chat") or {}).get("id",""))
        txt=str(msg.get("text") or "").strip()
        if incoming!=authorized:
            if incoming: send(token,incoming,"Unauthorized chat.")
            continue
        if txt.startswith("/"): handle_message(token,authorized,txt)
    # Acknowledge all processed updates on Telegram itself so the next scheduled
    # run cannot replay commands and dispatch duplicate reports.
    if max_update:
        telegram(token,"getUpdates",{"offset":max_update,"timeout":0,"limit":1})
    print(f"TELEGRAM_COMMANDS_OK: {len(updates)} update(s); acknowledged_through={max_update-1 if max_update else 'none'}")

if __name__=="__main__":
    main()
