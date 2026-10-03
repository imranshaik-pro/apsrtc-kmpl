/* Hub callback and over-grid branding. Does not change KPI values. */
function hubReportCallback_(e) {
  try {
    const b=JSON.parse(e&&e.postData&&e.postData.contents||'{}');
    const p=PropertiesService.getScriptProperties();
    const token=p.getProperty('HUB_CALLBACK_TOKEN');
    if(!token||b.token!==token) throw new Error('Unauthorized callback.');
    const row=Number(b.row);
    const hub=SpreadsheetApp.openById(p.getProperty('AUTOMATION_HUB_V2_RESPONSE_SHEET_ID'));
    const sheet=hub.getSheetByName('Automation Requests');
    if(!sheet||!Number.isInteger(row)||row<2||row>sheet.getLastRow()) throw new Error('Invalid Hub row.');
    const url=String(b.url||'');
    const sheetMatch=url.match(/^https:\/\/docs\.google\.com\/spreadsheets\/d\/([A-Za-z0-9_-]+)(?:\/(?:edit|view)(?:\?[A-Za-z0-9_=&%.-]*)?(?:#[A-Za-z0-9_=&%.-]*)?)?$/);
    const driveMatch=url.match(/^https:\/\/drive\.google\.com\/file\/d\/([A-Za-z0-9_-]+)\/view(?:\?[A-Za-z0-9_=&%.-]*)?$/);
    const annual=String(b.status||'').includes('ANNUAL KPI');
    if(!sheetMatch&&!driveMatch) throw new Error('Invalid report URL.');
    if(annual&&!sheetMatch) throw new Error('Annual report must be a spreadsheet.');
    if(annual) hubBrandAnnual_(SpreadsheetApp.openById(sheetMatch[1]));
    const headers=sheet.getRange(1,1,1,sheet.getLastColumn()).getDisplayValues()[0];
    let col=headers.indexOf('Drive Report Link')+1;
    if(!col){col=sheet.getLastColumn()+1;sheet.getRange(1,col).setValue('Drive Report Link');}
    sheet.getRange(row,col).setFormula('=HYPERLINK("'+b.url+'","Open Report")');
    if(b.status) hubStatus_(sheet,row,String(b.status));
    return ContentService.createTextOutput(JSON.stringify({ok:true,row:row})).setMimeType(ContentService.MimeType.JSON);
  } catch(err) {
    return ContentService.createTextOutput(JSON.stringify({ok:false,error:err.message})).setMimeType(ContentService.MimeType.JSON);
  }
}

function hubBrandAnnual_(report) {
  const targets=[['1. KPI Dashboard',14,220],['2. Detailed Data (Our Format)',1,180]];
  const sheets=targets.map(t=>({sheet:report.getSheetByName(t[0]),column:t[1],width:t[2]}));
  if(sheets.some(t=>!t.sheet)) throw new Error('Expected annual KPI sheets are missing.');
  const response=UrlFetchApp.fetch('https://www.apsrtc.ap.gov.in/images/apsrtc_logo1.gif',{muteHttpExceptions:true});
  if(response.getResponseCode()!==200) throw new Error('APSRTC logo download failed.');
  const blob=response.getBlob();
  if(!/^image\//.test(blob.getContentType())) throw new Error('APSRTC logo response is not an image.');
  sheets.forEach(t=>{
    const existing=t.sheet.getImages().filter(i=>i.getAltTextTitle()==='APSRTC report logo');
    let image=existing[0];
    if(!image) image=t.sheet.insertImage(blob,t.column,1,4,3);
    image.setAltTextTitle('APSRTC report logo').setAltTextDescription('Andhra Pradesh State Road Transport Corporation');
    image.setAnchorCell(t.sheet.getRange(1,t.column)).setAnchorCellXOffset(4).setAnchorCellYOffset(3);
    image.setWidth(t.width).setHeight(Math.round(t.width*130/640));
    existing.slice(1).forEach(i=>i.remove());
    const cell=t.sheet.getRange('N1');
    if(/^=IMAGE\(/i.test(cell.getFormula())) cell.clearContent();
  });
  SpreadsheetApp.flush();
}

function repairRajampetJuneLogo() {
  hubBrandAnnual_(SpreadsheetApp.openById('1HwHHeH7-Db-Dt2lioQwV1s07epxVrOgBRQlN_GhQwfU'));
  console.log('RAJAMPET_JUNE_OVER_GRID_LOGOS_INSTALLED');
}

function checkHubCallbackConfiguration() {
  const p=PropertiesService.getScriptProperties();
  console.log(JSON.stringify({hubSheetConfigured:!!p.getProperty('AUTOMATION_HUB_V2_RESPONSE_SHEET_ID'),callbackTokenConfigured:!!p.getProperty('HUB_CALLBACK_TOKEN')}));
}

