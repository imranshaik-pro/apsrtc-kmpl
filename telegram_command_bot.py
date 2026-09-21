"""Authorized Telegram menu/command processor for APSRTC automation."""
from __future__ import annotations
import json, os, re, urllib.parse, urllib.request
from datetime import date, datetime

API="https://api.telegram.org/bot{token}/{method}"
REPO=os.getenv("GITHUB_REPOSITORY","imranshaik-pro/apsrtc-kmpl")
REF=os.getenv("GITHUB_REF_NAME","master")
# Depot choices are supplied centrally through the DEPOT_MASTER GitHub variable.
# This avoids maintaining separate hard-coded lists in Telegram.
DEPOTS=tuple(d.strip().upper() for d in os.getenv("DEPOT_MASTER","").split("|") if d.strip())

def _request(url, *, data=None, headers=None):
    req=urllib.request.Request(url,data=data,headers=headers or {})
    with urllib.request.urlopen(req,timeout=25) as r: return json.load(r)

def telegram(token,method,params):
    return _request(API.format(token=token,method=method),data=urllib.parse.urlencode(params).encode())

def send(token,chat_id,text,keyboard=None,force_reply=False):
    p={"chat_id":chat_id,"text":text,"disable_web_page_preview":"true"}
    if keyboard: p["reply_markup"]=json.dumps({"inline_keyboard":keyboard})
    elif force_reply: p["reply_markup"]=json.dumps({"force_reply":True,"selective":True})
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
    if not DEPOTS:
        return [[{"text":"Depot master not configured","callback_data":"menu|status"}]]
    rows=[]
    for i in range(0,len(DEPOTS),2):
        rows.append([{"text":d,"callback_data":f"{action}|{d}"} for d in DEPOTS[i:i+2]])
    return rows

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

def event_type_keyboard(depot,vehicle):
    types=(("🔧 Unit Change","UNIT CHANGE"),("❌ Breakdown","BREAKDOWN"),("🛞 Tyre Change","TYRE CHANGE"),
           ("III Schedule III","SCHEDULE III"),("IV Schedule IV","SCHEDULE IV"))
    return [[{"text":label,"callback_data":f"etype|{depot}|{vehicle}|{value}"}] for label,value in types]

def post_event(payload):
    base=os.environ["VEHICLE_EVENTS_API_URL"].strip()
    key=os.environ["VEHICLE_EVENTS_API_KEY"].strip()
    sep="&" if "?" in base else "?"
    url=base+sep+urllib.parse.urlencode({"key":key})
    req=urllib.request.Request(url,data=json.dumps(payload).encode(),method="POST",
        headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=25) as r: result=json.load(r)
    if not result.get("ok"): raise RuntimeError(result.get("error") or "Vehicle Event API rejected event")
    return result

def event_detail_prompt(depot,vehicle,event_type,event_date):
    tag=f"EVENT DETAILS [{depot}|{vehicle}|{event_type}|{event_date}]"
    if event_type=="BREAKDOWN":
        guide="Reply: Location | KM Cancelled | Breakdown Details | Remarks"
    elif event_type=="TYRE CHANGE":
        guide="Reply: Position: Tyre No | Position: Tyre No | Remarks\nUse only FOS/FNS/ROSO/ROSI/RNSO/RNSI/SPARE positions."
    elif event_type=="UNIT CHANGE":
        guide="Reply: Components | Spring Positions | Remarks\nUse spring positions only FOS/FNS/ROS/RNS; use - when not applicable."
    else:
        guide="Reply with Remarks, or - if none."
    return tag+"\n"+guide

def parse_event_details(prompt,text):
    m=re.search(r"EVENT DETAILS \[([^|]+)\|([^|]+)\|([^|]+)\|([^\]]+)\]",prompt)
    if not m: return None
    depot,vehicle,event_type,event_date=m.groups()
    payload={"depot":depot,"vehicle_no":vehicle,"event_type":event_type,"event_date":event_date,
             "components":"","spring_positions":"","tyre_history":"","breakdown_location":"",
             "kms_cancelled":"","breakdown_details":"","remarks":""}
    if event_type=="BREAKDOWN":
        vals=[x.strip() for x in text.split("|",3)]
        if len(vals)<3: raise ValueError("Use: Location | KM Cancelled | Breakdown Details | Remarks")
        payload["breakdown_location"]=vals[0]; payload["kms_cancelled"]=vals[1]
        payload["breakdown_details"]=vals[2]; payload["remarks"]=vals[3] if len(vals)>3 else ""
    elif event_type=="UNIT CHANGE":
        vals=[x.strip() for x in text.split("|",2)]
        if len(vals)<1: raise ValueError("Enter component details.")
        payload["components"]="" if vals[0]=="-" else vals[0]
        payload["spring_positions"]="" if len(vals)<2 or vals[1]=="-" else vals[1]
        payload["remarks"]="" if len(vals)<3 or vals[2]=="-" else vals[2]
    elif event_type=="TYRE CHANGE":
        vals=[x.strip() for x in text.split("|")]
        tyre=[]; remarks=[]
        allowed={"FOS","FNS","ROSO","ROSI","RNSO","RNSI","SPARE"}
        for v in vals:
            if ":" in v and v.split(":",1)[0].strip().upper() in allowed: tyre.append(v)
            elif v and v!="-": remarks.append(v)
        if not tyre: raise ValueError("Enter at least one tyre as Position: Tyre No.")
        payload["tyre_history"]=" | ".join(tyre); payload["remarks"]=" | ".join(remarks)
    else:
        payload["remarks"]="" if text.strip()=="-" else text.strip()
    return payload

def confirmation_text(payload):
    packed=urllib.parse.quote(json.dumps(payload,separators=(",",":")),safe="")
    lines=["🛠 REVIEW VEHICLE EVENT",
      f"Depot: {payload['depot']}",f"Vehicle: {payload['vehicle_no']}",
      f"Date: {payload['event_date']}",f"Type: {payload['event_type']}"]
    for k,label in (("components","Components"),("spring_positions","Spring"),("tyre_history","Tyres"),
                    ("breakdown_location","Location"),("kms_cancelled","KM Cancelled"),
                    ("breakdown_details","Details"),("remarks","Remarks")):
        if payload.get(k): lines.append(f"{label}: {payload[k]}")
    lines += ["","Reply CONFIRM to save permanently, or CANCEL.","PAYLOAD:"+packed]
    return "\n".join(lines)

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
        send(token,chat_id,"Select depot for Vehicle Event:",depot_keyboard("event")); return
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
        send(token,chat_id,"Select depot for Vehicle Event:",depot_keyboard("event")); return
    if len(parts)==2 and parts[0]=="event" and parts[1] in DEPOTS:
        send(token,chat_id,f"VEHICLE NUMBER [{parts[1]}]\nReply with the vehicle number:",force_reply=True); return
    if len(parts)==4 and parts[0]=="etype" and parts[1] in DEPOTS:
        depot,vehicle,event_type=parts[1],normalize_vehicle(parts[2]),parts[3]
        today=date.today().isoformat()
        keyboard=[[{"text":"Today — "+today,"callback_data":f"edate|{depot}|{vehicle}|{event_type}|{today}"}]]
        send(token,chat_id,f"{event_type} — select Event Date:",keyboard); return
    if len(parts)==5 and parts[0]=="edate" and parts[1] in DEPOTS:
        send(token,chat_id,event_detail_prompt(parts[1],normalize_vehicle(parts[2]),parts[3],parts[4]),force_reply=True); return
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
        if txt.startswith("/"):
            handle_message(token,authorized,txt); continue
        reply=(msg.get("reply_to_message") or {}).get("text","")
        if reply.startswith("VEHICLE NUMBER ["):
            m=re.search(r"VEHICLE NUMBER \[([^\]]+)\]",reply)
            vehicle=normalize_vehicle(txt)
            if m and vehicle:
                send(token,authorized,f"Vehicle: {vehicle}\nSelect Event Type:",event_type_keyboard(m.group(1),vehicle))
            else: send(token,authorized,"Invalid vehicle number. Start /event again.",main_menu())
            continue
        if reply.startswith("EVENT DETAILS ["):
            try:
                payload=parse_event_details(reply,txt)
                send(token,authorized,confirmation_text(payload),force_reply=True)
            except ValueError as e: send(token,authorized,"❌ "+str(e)+"\nStart /event again.",main_menu())
            continue
        if reply.startswith("🛠 REVIEW VEHICLE EVENT"):
            if txt.upper()=="CANCEL":
                send(token,authorized,"Vehicle Event cancelled. Nothing was saved.",main_menu()); continue
            if txt.upper()!="CONFIRM":
                send(token,authorized,"Reply CONFIRM to save or CANCEL.",force_reply=True); continue
            m=re.search(r"PAYLOAD:(\S+)",reply)
            if not m:
                send(token,authorized,"Confirmation payload missing. Start /event again.",main_menu()); continue
            payload=json.loads(urllib.parse.unquote(m.group(1)))
            result=post_event(payload)
            send(token,authorized,f"✅ VEHICLE EVENT RECORDED\nEvent ID: {result.get('event_id')}\nDepot: {payload['depot']}\nVehicle: {payload['vehicle_no']}\nType: {payload['event_type']}",main_menu())
            continue
    # Acknowledge all processed updates on Telegram itself so the next scheduled
    # run cannot replay commands and dispatch duplicate reports.
    if max_update:
        telegram(token,"getUpdates",{"offset":max_update,"timeout":0,"limit":1})
    print(f"TELEGRAM_COMMANDS_OK: {len(updates)} update(s); acknowledged_through={max_update-1 if max_update else 'none'}")

if __name__=="__main__":
    main()
