const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const code=fs.readFileSync(__dirname+'/../apps-script/report_branding.gs','utf8');
let opens=0,writes=0;
const context={PropertiesService:{getScriptProperties:()=>({getProperty:k=>k==='HUB_CALLBACK_TOKEN'?'test-token':'hub-id'})},SpreadsheetApp:{openById:()=>{opens++;return {getSheetByName:()=>({getLastRow:()=>18})};}},ContentService:{MimeType:{JSON:'json'},createTextOutput:text=>({setMimeType:()=>JSON.parse(text)})},console};
vm.createContext(context);vm.runInContext(code,context);
function call(body){return context.hubReportCallback_({postData:{contents:JSON.stringify(body)}});}
assert.equal(call({token:'wrong',row:18,url:'https://docs.google.com/spreadsheets/d/test/edit'}).ok,false);
assert.equal(opens,0,'unauthenticated request must not open Sheets');
assert.equal(call({token:'test-token',row:18.5,url:'https://docs.google.com/spreadsheets/d/test/edit'}).ok,false);
assert.equal(call({token:'test-token',row:19,url:'https://docs.google.com/spreadsheets/d/test/edit'}).ok,false);
assert.equal(call({token:'test-token',row:18,url:'https://example.com/anything'}).ok,false);
assert.equal(opens,3,'invalid report URL must not open report');
assert.equal(call({token:'test-token',row:18,url:'https://docs.google.com/spreadsheets/d/test/edit\"malicious'}).ok,false);
assert.equal(call({token:'test-token',row:18,url:'https://drive.google.com/file/d/test/view',status:'COMPLETED | ANNUAL KPI'}).ok,false);
let reportOpens=0,link='';
const hubSheet={getLastRow:()=>18,getLastColumn:()=>2,getRange:(r,c)=>({
  getDisplayValues:()=>[['Automation Status','Drive Report Link']],
  setFormula:value=>{link=value;},setValue:()=>{}
})};
context.SpreadsheetApp.openById=id=>{if(id!=='hub-id'){reportOpens++;throw Error('Daily report must not be opened as a spreadsheet');}return {getSheetByName:()=>hubSheet};};
context.hubStatus_=()=>{};
assert.equal(call({token:'test-token',row:18,url:'https://drive.google.com/file/d/daily-file/view?usp=drivesdk',status:'COMPLETED | DAILY'}).ok,true);
assert.equal(reportOpens,0);
assert.ok(link.includes('daily-file/view'));
assert.equal(call({token:'test-token',row:18,url:'https://docs.google.com/spreadsheets/d/monthly-sheet/edit',status:'COMPLETED | MONTHLY'}).ok,true);
assert.equal(reportOpens,0);
const sheets=['1. KPI Dashboard','2. Detailed Data (Our Format)'].map(name=>{
  const images=[];let formula=name.startsWith('1.')?'=IMAGE("old")':'';
  return {name,images,getImages:()=>images,getRange:(r,c)=>({getFormula:()=>formula,clearContent:()=>{formula='';writes++;}}),insertImage:()=>{
    const image={getAltTextTitle:()=>image.title,remove:()=>images.splice(images.indexOf(image),1)};
    for(const method of ['setAltTextTitle','setAltTextDescription','setAnchorCell','setAnchorCellXOffset','setAnchorCellYOffset','setWidth','setHeight'])image[method]=value=>{if(method==='setAltTextTitle')image.title=value;return image;};
    images.push(image);return image;
  }};
});
context.UrlFetchApp={fetch:()=>({getResponseCode:()=>200,getBlob:()=>({getContentType:()=> 'image/gif'})})};
context.SpreadsheetApp.flush=()=>{};
const report={getSheetByName:name=>sheets.find(s=>s.name===name)};
context.hubBrandAnnual_(report);context.hubBrandAnnual_(report);
assert.deepEqual(sheets.map(s=>s.images.length),[1,1],'repeat branding must not duplicate logos');
assert.equal(writes,1,'only the previous IMAGE formula may be cleared');
console.log('Callback authentication, row bounds, report URL and branding idempotency passed');
