/* APSRTC Automation Hub
 * Single Google Form dispatcher for Daily, Monthly and Annual KPI reports.
 * Vehicle Event remains on the same hub roadmap but uses its permanent register/API.
 * Script Property required: GITHUB_TOKEN
 */
const HUB={
  REPO:'imranshaik-pro/apsrtc-kmpl',BRANCH:'master',TZ:'Asia/Kolkata',
  ACTIONS:{
    'DAILY HSD KMPL REPORT':'daily-report.yml',
    'MONTHLY PERFORMANCE REPORT':'monthly-report.yml',
    'ANNUAL KPI REPORT':'annual-kpi.yml'
  }
};

function onHubSubmit(e){
  if(!e||!e.range) throw new Error('Run from spreadsheet Form Submit trigger.');
  const sheet=e.range.getSheet(), row=e.range.getRow(), named=e.namedValues||{};
  try{
    const action=hubPick_(named,['Required Service / Report','Action / Report Type','Action','Report Type']).toUpperCase();
    const depot=hubPick_(named,['Depot']).toUpperCase();
    if(!action) throw new Error('Required Service / Report is missing.');
    if(!depot) throw new Error('Depot is missing.');

    if(action==='DAILY HSD KMPL REPORT'){
      const raw=hubPick_(named,['Date','Report Date']);
      if(!raw) throw new Error('Report Date is missing.');
      const d=hubDate_(raw), today=Utilities.formatDate(new Date(),HUB.TZ,'yyyy-MM-dd');
      if(d>today) throw new Error("Can't retrieve future-date data.");
      hubDispatch_('daily-report.yml',{depot:depot,report_date:d});
      hubStatus_(sheet,row,'SUBMITTED | DAILY | '+depot+' | '+d); return;
    }

    if(action==='MONTHLY PERFORMANCE REPORT'){
      const raw=hubPick_(named,['Month','Report Month','Selected Month']);
      if(!raw) throw new Error('Report Month is missing.');
      const m=hubMonth_(raw), current=Utilities.formatDate(new Date(),HUB.TZ,'yyyy-MM');
      if(m>current) throw new Error("Can't retrieve future-month data.");
      hubDispatch_('monthly-report.yml',{depot:depot,month:m});
      hubStatus_(sheet,row,'SUBMITTED | MONTHLY | '+depot+' | '+m); return;
    }

    if(action==='ANNUAL KPI REPORT'){
      const raw=hubPick_(named,['Month','Selected Month','Report Month']);
      if(!raw) throw new Error('Selected Month is missing.');
      const m=hubMonth_(raw), current=Utilities.formatDate(new Date(),HUB.TZ,'yyyy-MM');
      if(m>current) throw new Error("Can't retrieve future-month data.");
      const fy=hubFY_(m);
      hubDispatch_('annual-kpi.yml',{depot:depot,selected_month:m,financial_years:fy});
      hubStatus_(sheet,row,'SUBMITTED | ANNUAL KPI | '+depot+' | '+m+' | FY '+fy); return;
    }

    if(action==='VEHICLE EVENT ENTRY'){
      hubRecordVehicleEvent_(named,sheet,row,depot);
      return;
    }
    if(action==='VEHICLE 360 HISTORY'){
      hubStatus_(sheet,row,'VEHICLE 360 PHASE 2');
      throw new Error('Vehicle 360 Hub lookup will be enabled in Phase 2.');
    }
    throw new Error('Unsupported Action / Report Type: '+action);
  }catch(err){hubStatus_(sheet,row,'ERROR: '+err.message);throw err;}
}

function setupHubV2Trigger(){
  const id=PropertiesService.getScriptProperties().getProperty('AUTOMATION_HUB_V2_RESPONSE_SHEET_ID');
  if(!id) throw new Error('AUTOMATION_HUB_V2_RESPONSE_SHEET_ID is missing.');
  ScriptApp.getProjectTriggers().forEach(t=>{if(t.getHandlerFunction()==='onHubSubmit')ScriptApp.deleteTrigger(t);});
  ScriptApp.newTrigger('onHubSubmit').forSpreadsheet(SpreadsheetApp.openById(id)).onFormSubmit().create();
  console.log('AUTOMATION_HUB_V2_TRIGGER_INSTALLED');
}

function hubDispatch_(workflow,inputs){
  const token=PropertiesService.getScriptProperties().getProperty('GITHUB_TOKEN');
  if(!token) throw new Error('GITHUB_TOKEN is missing from Script Properties.');
  const url='https://api.github.com/repos/'+HUB.REPO+'/actions/workflows/'+workflow+'/dispatches';
  const r=UrlFetchApp.fetch(url,{method:'post',contentType:'application/json',
    headers:{Authorization:'Bearer '+token,Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'},
    payload:JSON.stringify({ref:HUB.BRANCH,inputs:inputs}),muteHttpExceptions:true});
  if(r.getResponseCode()!==204) throw new Error('GitHub dispatch failed ('+r.getResponseCode()+'): '+r.getContentText());
}
function hubPick_(named,headers){
  const norm=v=>String(v||'').trim().toLowerCase().replace(/[^a-z0-9]+/g,' ').replace(/\s+/g,' ').trim();
  const entries=Object.keys(named).map(k=>({k:k,n:norm(k)}));
  for(const h of headers){const x=entries.find(e=>e.n===norm(h));if(x){const v=named[x.k];return Array.isArray(v)?String(v[0]||'').trim():String(v||'').trim();}}
  return '';
}
function hubDate_(raw){
  const s=String(raw).trim();let m=s.match(/^(\d{4})-(\d{1,2})-(\d{1,2})$/);
  if(m)return m[1]+'-'+String(m[2]).padStart(2,'0')+'-'+String(m[3]).padStart(2,'0');
  m=s.match(/^(\d{1,2})[\/-](\d{1,2})[\/-](\d{4})$/);
  if(m)return m[3]+'-'+String(m[2]).padStart(2,'0')+'-'+String(m[1]).padStart(2,'0');
  const d=new Date(s);if(isNaN(d.getTime()))throw new Error('Invalid date: '+s);
  return Utilities.formatDate(d,HUB.TZ,'yyyy-MM-dd');
}
function hubMonth_(raw){
  const s=String(raw).trim();let m=s.match(/^(20\d{2})[-\/]([01]?\d)$/);
  if(m&&+m[2]>=1&&+m[2]<=12)return m[1]+'-'+String(+m[2]).padStart(2,'0');
  m=s.match(/^([A-Za-z]{3,9})[\s\-\/]+(20\d{2})$/);
  if(m){const a=['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'],i=a.indexOf(m[1].slice(0,3).toLowerCase());if(i>=0)return m[2]+'-'+String(i+1).padStart(2,'0');}
  m=s.match(/^([01]?\d)[\s\-\/]+(20\d{2})$/);
  if(m&&+m[1]>=1&&+m[1]<=12)return m[2]+'-'+String(+m[1]).padStart(2,'0');
  throw new Error('Invalid month: '+s);
}
function hubFY_(m){const p=m.split('-'),y=+p[0],mo=+p[1],s=mo>=4?y:y-1;return s+'-'+String(s+1).slice(-2);}
function hubStatus_(sheet,row,status){
  const h=sheet.getRange(1,1,1,sheet.getLastColumn()).getDisplayValues()[0];let c=h.indexOf('Automation Status')+1;
  if(!c){c=sheet.getLastColumn()+1;sheet.getRange(1,c).setValue('Automation Status').setFontWeight('bold').setBackground('#0B3D78').setFontColor('#FFFFFF');}
  sheet.getRange(row,c).setValue(status);
}

/* Professional response-sheet presentation. Keeps raw response columns intact. */
function formatAutomationHubSheet(){
  const s=SpreadsheetApp.getActiveSpreadsheet().getActiveSheet(),lastCol=s.getLastColumn(),lastRow=Math.max(s.getLastRow(),2);
  s.setHiddenGridlines(true);s.setFrozenRows(1);s.setRowHeight(1,38);
  s.getRange(1,1,1,lastCol).setBackground('#0B3D78').setFontColor('#FFFFFF').setFontWeight('bold')
    .setFontSize(11).setHorizontalAlignment('center').setVerticalAlignment('middle');
  s.getRange(2,1,lastRow-1,lastCol).setVerticalAlignment('middle').setWrap(true);
  s.getRange(1,1,lastRow,lastCol).setBorder(true,true,true,true,true,true,'#C7D5E8',SpreadsheetApp.BorderStyle.SOLID);
  for(let c=1;c<=lastCol;c++)s.setColumnWidth(c,c===1?155:180);
  if(lastRow>2)s.getRange(2,1,lastRow-1,lastCol).applyRowBanding(SpreadsheetApp.BandingTheme.LIGHT_GREY,false,false);
}

function hubRecordVehicleEvent_(named,hubSheet,hubRow,depot){
  const eventDateRaw=hubPick_(named,['Event Date']);
  const vehicleNo=normalizeVehicle_(hubPick_(named,['Vehicle No']));
  const eventType=normalizeEventType_(hubPick_(named,['Event Type']));
  if(!eventDateRaw||!vehicleNo||!eventType) throw new Error('Vehicle Event requires Event Date, Vehicle No and Event Type.');
  const eventDate=parseEventDate_(eventDateRaw);
  if(!eventDate) throw new Error('Invalid Event Date: '+eventDateRaw);
  const allowed=['UNIT CHANGE','BREAKDOWN','TYRE CHANGE','SCHEDULE III','SCHEDULE IV'];
  if(!allowed.includes(eventType)) throw new Error('Unsupported Event Type: '+eventType);
  const register=SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Vehicle Events');
  if(!register) throw new Error('Vehicle Events permanent register not found.');
  const row=register.getLastRow()+1;
  const eventDateISO=Utilities.formatDate(eventDate,HUB.TZ,'yyyy-MM-dd');
  const createdAt=Utilities.formatDate(new Date(),HUB.TZ,'yyyy-MM-dd HH:mm:ss');
  // Full normalized depot slug prevents collisions between depots sharing first letters.
  const depotCode=depot.replace(/[^A-Z0-9]+/g,'-').replace(/^-|-$/g,'')||'DEPOT';
  const eventId=[depotCode,Utilities.formatDate(eventDate,HUB.TZ,'yyyyMMdd'),vehicleNo,'R'+String(row).padStart(4,'0'),Utilities.formatDate(new Date(),HUB.TZ,'HHmmss')].join('-');
  const components=hubPick_(named,['Component/Aggregate']);
  const springs=hubPick_(named,['Spring Assembly Change Position']);
  const tyrePositions=String(hubPick_(named,['Tyres Change Position'])||'').split(',').map(x=>x.trim()).filter(Boolean);
  const tyreHistory=tyrePositions.map(p=>{
    const label=p.toUpperCase()==='SPARE'?'Spare':p.toUpperCase();
    const no=hubPick_(named,[label+' Tyre No']);
    return label.toUpperCase()+': '+(no||'TYRE NO NOT ENTERED');
  }).join(' | ');
  const fields={
    'Event ID':eventId,'Depot':depot,'Created At':createdAt,'Entry Source':'AUTOMATION_HUB',
    'Normalized Event Date':eventDateISO,'Normalized Vehicle No':vehicleNo,'Normalized Event Type':eventType,
    'Components':components,'Spring Positions':springs,'Tyre History':tyreHistory,
    'Breakdown Location':hubPick_(named,['Break Down Location']),'KM Cancelled':hubPick_(named,['KMs Canceled']),
    'Breakdown Details':hubPick_(named,['Break Down Details']),'Event Remarks':hubPick_(named,['Remarks']),
    'Automation Status':'EVENT RECORDED'
  };
  Object.keys(fields).forEach(h=>setAuditValue_(register,row,h,fields[h]));
  dispatchToGitHub_({
    event_id:eventId,created_at:createdAt,event_date:eventDateISO,depot:depot,vehicle_no:vehicleNo,event_type:eventType,
    components:components,spring_positions:springs,tyre_history:tyreHistory,breakdown_location:fields['Breakdown Location'],
    kms_cancelled:String(fields['KM Cancelled']||''),breakdown_details:fields['Breakdown Details'],remarks:fields['Event Remarks'],
    entry_source:'AUTOMATION_HUB'
  });
  setAuditValue_(register,row,'GitHub Dispatch Status','DISPATCHED');
  hubStatus_(hubSheet,hubRow,'RECORDED | VEHICLE EVENT | '+depot+' | '+eventId);
}
