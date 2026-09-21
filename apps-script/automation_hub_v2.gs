/* APSRTC Automation Hub V2 — clean one-time builder
 * Creates a fresh Hub because Google Forms cannot reliably restructure an
 * already-branched form in place. Existing operational forms are untouched.
 * Run: buildCleanApsrtcAutomationHubV2()
 */
function buildCleanApsrtcAutomationHubV2(){
  const source=SpreadsheetApp.getActiveSpreadsheet();
  const master=source.getSheetByName('Depot Master');
  if(!master||master.getLastRow()<2) throw new Error('Depot Master is missing or empty.');
  const depots=[...new Set(master.getRange(2,1,master.getLastRow()-1,1).getDisplayValues().flat()
    .map(v=>String(v||'').trim().toUpperCase()).filter(Boolean))];
  if(!depots.length) throw new Error('Depot Master contains no depots.');

  const form=FormApp.create('APSRTC – OPERATIONS & KPI AUTOMATION HUB');
  form.setDescription(
    'ANDHRA PRADESH STATE ROAD TRANSPORT CORPORATION (APSRTC)\n' +
    'Unified Depot Operations, KMPL, KPI & Vehicle Automation Portal\n\n' +
    'Select Depot → Select Required Service → Enter relevant details → Submit'
  ).setConfirmationMessage('Request received successfully. Please refer to the Automation Hub Register for processing status.')
   .setProgressBar(true).setShuffleQuestions(false);

  // LANDING PAGE: depot first, service second.
  form.addSectionHeaderItem().setTitle('DEPOT & SERVICE SELECTION')
    .setHelpText('Select the operating depot first, then choose the required report or vehicle service.');
  form.addListItem().setTitle('Depot').setChoiceValues(depots).setRequired(true);
  const service=form.addMultipleChoiceItem().setTitle('Required Service / Report').setRequired(true);

  // DAILY
  const daily=form.addPageBreakItem().setTitle('DAILY HSD KMPL REPORT')
    .setHelpText('Generate the Daily HSD KMPL report for the selected depot.');
  form.addDateItem().setTitle('Report Date').setIncludesYear(true).setRequired(true);

  // MONTHLY
  const monthly=form.addPageBreakItem().setTitle('MONTHLY PERFORMANCE REPORT')
    .setHelpText('Generate or refresh the selected depot monthly performance report.');
  form.addDateItem().setTitle('Report Month').setIncludesYear(true).setRequired(true);

  // ANNUAL
  const annual=form.addPageBreakItem().setTitle('ANNUAL KPI REPORT')
    .setHelpText('Generate the KPI report through the selected month. Financial year is derived automatically.');
  form.addDateItem().setTitle('Selected Month').setIncludesYear(true).setRequired(true);

  // VEHICLE EVENT
  const event=form.addPageBreakItem().setTitle('VEHICLE EVENT ENTRY')
    .setHelpText('Record a permanent operational event against the selected depot and vehicle.');
  form.addDateItem().setTitle('Event Date').setIncludesYear(true).setRequired(true);
  form.addTextItem().setTitle('Vehicle No').setHelpText('AP prefix is optional.').setRequired(true);
  form.addMultipleChoiceItem().setTitle('Event Type').setChoiceValues(
    ['UNIT CHANGE','BREAKDOWN','TYRE CHANGE','SCHEDULE III','SCHEDULE IV']).setRequired(true);
  form.addCheckboxItem().setTitle('Component/Aggregate').setChoiceValues([
    'Engine','TO','Cylinder Head','FIP','Injectors','Air Compressor','AC Head','Flywheel',
    'Gear Box','I Beam','Drive Head','FC Unit','Water Pump','Cooler Plate','PP Shaft Set',
    'Vane Pump','Radiator','Clutch Plate','Clutch Springer','Spring Change (mention with Position)','Other'
  ]);
  form.addCheckboxItem().setTitle('Spring Assembly Change Position').setChoiceValues(['FOS','FNS','ROS','RNS']);
  form.addCheckboxItem().setTitle('Tyres Change Position').setChoiceValues(['FOS','FNS','ROSI','ROSO','RNSO','RNSI','Spare']);
  ['FOS','FNS','ROSI','ROSO','RNSO','RNSI','Spare'].forEach(p=>form.addTextItem().setTitle(p+' Tyre No'));
  form.addTextItem().setTitle('Break Down Location');
  form.addTextItem().setTitle('KMs Canceled');
  form.addParagraphTextItem().setTitle('Break Down Details');
  form.addParagraphTextItem().setTitle('Remarks');

  // VEHICLE 360
  const v360=form.addPageBreakItem().setTitle('VEHICLE 360° HISTORY')
    .setHelpText('Request consolidated vehicle history for the selected depot.');
  form.addTextItem().setTitle('Vehicle 360 - Vehicle No').setHelpText('AP prefix is optional.').setRequired(true);

  // Branch once, from the landing page. Each service section submits directly.
  service.setChoices([
    service.createChoice('Daily HSD KMPL Report',daily),
    service.createChoice('Monthly Performance Report',monthly),
    service.createChoice('Annual KPI Report',annual),
    service.createChoice('Vehicle Event Entry',event),
    service.createChoice('Vehicle 360° History',v360)
  ]);
  [daily,monthly,annual,event,v360].forEach(section=>section.setGoToPage(FormApp.PageNavigationType.SUBMIT));

  const responses=SpreadsheetApp.create('APSRTC – AUTOMATION HUB REGISTER');
  form.setDestination(FormApp.DestinationType.SPREADSHEET,responses.getId());
  Utilities.sleep(1500);
  const sheet=responses.getSheets()[0];
  sheet.setName('Automation Requests');
  styleCleanHubRegister_(sheet);

  PropertiesService.getScriptProperties().setProperties({
    AUTOMATION_HUB_V2_FORM_ID:form.getId(),
    AUTOMATION_HUB_V2_FORM_EDIT_URL:form.getEditUrl(),
    AUTOMATION_HUB_V2_FORM_URL:form.getPublishedUrl(),
    AUTOMATION_HUB_V2_RESPONSE_SHEET_ID:responses.getId()
  },false);

  console.log('CLEAN_AUTOMATION_HUB_V2_CREATED');
  console.log('FORM_EDIT_URL: '+form.getEditUrl());
  console.log('FORM_URL: '+form.getPublishedUrl());
  console.log('RESPONSE_SHEET_URL: '+responses.getUrl());
}

function styleCleanHubRegister_(sheet){
  sheet.setHiddenGridlines(true);
  sheet.setFrozenRows(1);
  sheet.setRowHeight(1,42);
  const cols=Math.max(sheet.getLastColumn(),sheet.getMaxColumns());
  sheet.getRange(1,1,1,cols).setBackground('#123B69').setFontColor('#FFFFFF')
    .setFontWeight('bold').setFontSize(11).setHorizontalAlignment('center').setVerticalAlignment('middle');
  for(let c=1;c<=cols;c++) sheet.setColumnWidth(c,c===1?165:190);
}
