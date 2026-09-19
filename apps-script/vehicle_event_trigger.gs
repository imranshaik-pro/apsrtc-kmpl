/* APSRTC Vehicle Event Register - Google Form / Response Sheet trigger
 * Bind this script to the VEHICLE EVENT response spreadsheet.
 * Script Property required: GITHUB_TOKEN
 * The sheet remains the permanent append-only register; this trigger dispatches
 * the normalized event to GitHub for validation and downstream Vehicle 360 use.
 */

const REPO = 'imranshaik-pro/apsrtc-kmpl';
const WORKFLOW = 'vehicle-event.yml';
const BRANCH = 'master';
const TZ = 'Asia/Kolkata';

function onVehicleEventSubmit(e) {
  const sheet = e.range.getSheet();
  const row = e.range.getRow();
  const named = e.namedValues || {};
  try {
    const eventDate = normalizeDate_(pickValue_(named, ['event date', 'date']));
    const depot = pickValue_(named, ['depot']) || 'PRODDUTUR';
    const vehicleNo = pickValue_(named, ['vehicle no', 'vehicle']);
    const eventType = normalizeEventType_(pickValue_(named, ['event type', 'event']));
    const component = pickValue_(named, ['component', 'aggregate']);
    const tyrePosition = pickValue_(named, ['tyre position', 'tire position']);
    const tyreNo = pickValue_(named, ['tyre no', 'tire no']);
    const breakdownDetails = pickValue_(named, ['breakdown details', 'breakdown']);
    const remarks = pickValue_(named, ['remarks', 'remark']);

    if (!eventDate) throw new Error('Event Date was not found.');
    if (!vehicleNo) throw new Error('Vehicle No was not found.');
    if (!['UNIT CHANGE','BREAKDOWN','TYRE CHANGE'].includes(eventType))
      throw new Error('Unsupported Event Type: ' + eventType);
    if (eventType === 'UNIT CHANGE' && !component)
      throw new Error('Component / Aggregate is required for Unit Change.');

    dispatch_(WORKFLOW, {
      event_date: eventDate,
      depot: depot.toUpperCase(),
      vehicle_no: vehicleNo.replace(/\s+/g, '').toUpperCase(),
      event_type: eventType,
      component: component,
      tyre_position: tyrePosition,
      tyre_no: tyreNo,
      breakdown_details: breakdownDetails,
      remarks: remarks
    });
    setStatus_(sheet,row,'Submitted to Event Engine');
  } catch (err) {
    setStatus_(sheet,row,'ERROR: ' + err.message);
    throw err;
  }
}

function setupVehicleEventTrigger() {
  deleteTriggers_('onVehicleEventSubmit');
  ScriptApp.newTrigger('onVehicleEventSubmit')
    .forSpreadsheet(SpreadsheetApp.getActive())
    .onFormSubmit()
    .create();
}

function normalizeEventType_(raw) {
  const v=String(raw||'').trim().toUpperCase().replace(/\s+/g,' ');
  const aliases={'UNIT':'UNIT CHANGE','AGGREGATE CHANGE':'UNIT CHANGE','COMPONENT CHANGE':'UNIT CHANGE','TYRE':'TYRE CHANGE','TIRE CHANGE':'TYRE CHANGE'};
  return aliases[v] || v;
}

function dispatch_(workflow, inputs) {
  const token=PropertiesService.getScriptProperties().getProperty('GITHUB_TOKEN');
  if (!token) throw new Error('GITHUB_TOKEN is missing from Script Properties.');
  const url='https://api.github.com/repos/'+REPO+'/actions/workflows/'+workflow+'/dispatches';
  const response=UrlFetchApp.fetch(url,{method:'post',contentType:'application/json',headers:{Authorization:'Bearer '+token,Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'},payload:JSON.stringify({ref:BRANCH,inputs:inputs}),muteHttpExceptions:true});
  if (response.getResponseCode()!==204) throw new Error('GitHub dispatch failed ('+response.getResponseCode()+'): '+response.getContentText());
}

function pickValue_(named, keywords) {
  const keys=Object.keys(named);
  for (const keyword of keywords) {
    const match=keys.find(k=>k.toLowerCase().includes(keyword));
    if (match) { const value=named[match]; return Array.isArray(value)?String(value[0]).trim():String(value).trim(); }
  }
  return '';
}

function normalizeDate_(raw) {
  raw=String(raw||'').trim(); if(!raw) return '';
  let m=raw.match(/^(\d{4})-(\d{1,2})-(\d{1,2})$/);
  if(m) return m[1]+'-'+pad2_(m[2])+'-'+pad2_(m[3]);
  m=raw.match(/^(\d{1,2})[\/-](\d{1,2})[\/-](\d{4})$/);
  if(m) return m[3]+'-'+pad2_(m[2])+'-'+pad2_(m[1]);
  const d=new Date(raw); if(isNaN(d.getTime())) throw new Error('Invalid date: '+raw);
  return Utilities.formatDate(d,TZ,'yyyy-MM-dd');
}

function setStatus_(sheet,row,status) {
  const values=sheet.getRange(1,1,1,sheet.getLastColumn()).getValues()[0];
  let col=values.findIndex(v=>String(v).trim()==='Automation Status')+1;
  if(!col){col=sheet.getLastColumn()+1;sheet.getRange(1,col).setValue('Automation Status');}
  sheet.getRange(row,col).setValue(status);
}

function deleteTriggers_(handler) {
  ScriptApp.getProjectTriggers().forEach(t=>{if(t.getHandlerFunction()===handler) ScriptApp.deleteTrigger(t);});
}
function pad2_(v){return String(v).padStart(2,'0');}
