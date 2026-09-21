/* APSRTC Automation Hub Builder
 * Run buildApsrtcAutomationHub() once from the existing Vehicle Event
 * spreadsheet-bound Apps Script. It reads Depot Master, creates a new unified
 * Google Form + linked response spreadsheet, and installs the Hub dispatcher.
 */
function buildApsrtcAutomationHub() {
  const source = SpreadsheetApp.getActiveSpreadsheet();
  const master = source.getSheetByName('Depot Master');
  if (!master || master.getLastRow() < 2) throw new Error('Depot Master is missing or empty.');

  const depots = [...new Set(master.getRange(2,1,master.getLastRow()-1,1)
    .getDisplayValues().flat().map(v=>String(v||'').trim().toUpperCase()).filter(Boolean))];
  if (!depots.length) throw new Error('No depots found in Depot Master.');

  const form = FormApp.create('APSRTC – OPERATIONS & KPI AUTOMATION HUB');
  form.setDescription(
    'ANDHRA PRADESH STATE ROAD TRANSPORT CORPORATION (APSRTC)\n' +
    'Unified Operations, Vehicle Events, KMPL Reporting & KPI Automation Portal\n\n' +
    'Select the required service. Only the relevant fields will be shown.'
  );
  form.setConfirmationMessage('Request received successfully. Processing status will be recorded in the Automation Hub response register.');
  form.setProgressBar(true);
  form.setShuffleQuestions(false);

  const action = form.addMultipleChoiceItem().setTitle('Action / Report Type').setRequired(true);

  const daily = form.addPageBreakItem().setTitle('DAILY HSD KMPL REPORT')
    .setHelpText('Generate the Daily HSD KMPL report for the selected depot and date.');
  form.addListItem().setTitle('Daily - Depot').setChoiceValues(depots).setRequired(true);
  form.addDateItem().setTitle('Report Date').setIncludesYear(true).setRequired(true);
  const dailyEnd=form.addPageBreakItem().setTitle('Daily Request Complete');

  const monthly = form.addPageBreakItem().setTitle('MONTHLY PERFORMANCE REPORT')
    .setHelpText('Generate or refresh the monthly performance report. Open-month and closed-month business rules remain unchanged.');
  form.addListItem().setTitle('Monthly - Depot').setChoiceValues(depots).setRequired(true);
  form.addDateItem().setTitle('Report Month').setIncludesYear(true).setRequired(true);
  const monthlyEnd=form.addPageBreakItem().setTitle('Monthly Request Complete');

  const annual = form.addPageBreakItem().setTitle('ANNUAL KPI REPORT')
    .setHelpText('Generate the Annual KPI report through the selected month. Financial year is determined automatically.');
  form.addListItem().setTitle('Annual - Depot').setChoiceValues(depots).setRequired(true);
  form.addDateItem().setTitle('Selected Month').setIncludesYear(true).setRequired(true);
  const annualEnd=form.addPageBreakItem().setTitle('Annual KPI Request Complete');

  const event = form.addPageBreakItem().setTitle('VEHICLE EVENT ENTRY')
    .setHelpText('Record a permanent vehicle event. The event is written to the Vehicle Event Register.');
  form.addListItem().setTitle('Vehicle Event - Depot').setChoiceValues(depots).setRequired(true);
  form.addDateItem().setTitle('Event Date').setIncludesYear(true).setRequired(true);
  form.addTextItem().setTitle('Vehicle No').setRequired(true);
  form.addMultipleChoiceItem().setTitle('Event Type').setChoiceValues(
    ['UNIT CHANGE','BREAKDOWN','TYRE CHANGE','SCHEDULE III','SCHEDULE IV']).setRequired(true);
  form.addCheckboxItem().setTitle('Component/Aggregate').setChoiceValues([
    'Engine','TO','Cylinder Head','FIP','Injectors','Air Compressor','AC Head','Flywheel',
    'Gear Box','I Beam','Drive Head','FC Unit','Water Pump','Cooler Plate','PP Shaft Set',
    'Vane Pump','Radiator','Clutch Plate','Clutch Springer','Spring Change (mention with Position)','Other'
  ]);
  form.addCheckboxItem().setTitle('Spring Assembly Change Position').setChoiceValues(['FOS','FNS','ROS','RNS']);
  form.addCheckboxItem().setTitle('Tyres Change Position').setChoiceValues(['FOS','FNS','ROSO','ROSI','RNSO','RNSI','SPARE']);
  ['FOS','FNS','ROSO','ROSI','RNSO','RNSI','Spare'].forEach(p=>form.addTextItem().setTitle(p+' Tyre No'));
  form.addTextItem().setTitle('Break Down Location');
  form.addTextItem().setTitle('KMs Canceled');
  form.addParagraphTextItem().setTitle('Break Down Details');
  form.addParagraphTextItem().setTitle('Remarks');
  const eventEnd=form.addPageBreakItem().setTitle('Vehicle Event Complete');

  const vehicle = form.addPageBreakItem().setTitle('VEHICLE 360° HISTORY')
    .setHelpText('Vehicle 360° lookup interface. Backend activation follows after Hub report validation.');
  form.addListItem().setTitle('Vehicle 360 - Depot').setChoiceValues(depots).setRequired(true);
  form.addTextItem().setTitle('Vehicle 360 - Vehicle No').setRequired(true);
  const vehicleEnd=form.addPageBreakItem().setTitle('Vehicle 360 Request Complete');

  // Branch from the landing page. Each terminal section submits instead of
  // falling through into the next service.
  action.setChoices([
    action.createChoice('Daily HSD KMPL Report', daily),
    action.createChoice('Monthly Performance Report', monthly),
    action.createChoice('Annual KPI Report', annual),
    action.createChoice('Vehicle Event Entry', event),
    action.createChoice('Vehicle 360° History', vehicle)
  ]);
  daily.setGoToPage(FormApp.PageNavigationType.CONTINUE);
  dailyEnd.setGoToPage(FormApp.PageNavigationType.SUBMIT);
  monthlyEnd.setGoToPage(FormApp.PageNavigationType.SUBMIT);
  annualEnd.setGoToPage(FormApp.PageNavigationType.SUBMIT);
  eventEnd.setGoToPage(FormApp.PageNavigationType.SUBMIT);
  vehicleEnd.setGoToPage(FormApp.PageNavigationType.SUBMIT);

  const responses = SpreadsheetApp.create('APSRTC – AUTOMATION HUB REGISTER');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, responses.getId());
  Utilities.sleep(1500);
  const responseSheet=responses.getSheets()[0];
  responseSheet.setName('Automation Requests');
  formatHubRegister_(responseSheet);

  const props=PropertiesService.getScriptProperties();
  props.setProperties({
    AUTOMATION_HUB_FORM_ID:form.getId(),
    AUTOMATION_HUB_FORM_EDIT_URL:form.getEditUrl(),
    AUTOMATION_HUB_FORM_URL:form.getPublishedUrl(),
    AUTOMATION_HUB_RESPONSE_SHEET_ID:responses.getId()
  },false);

  console.log('AUTOMATION_HUB_CREATED');
  console.log('FORM_EDIT_URL: '+form.getEditUrl());
  console.log('FORM_URL: '+form.getPublishedUrl());
  console.log('RESPONSE_SHEET_URL: '+responses.getUrl());
}

function formatHubRegister_(sheet) {
  sheet.setHiddenGridlines(true);
  sheet.setFrozenRows(1);
  sheet.setRowHeight(1,40);
  const maxCols=Math.max(sheet.getMaxColumns(),1);
  sheet.getRange(1,1,1,maxCols).setBackground('#0B3D78').setFontColor('#FFFFFF')
    .setFontWeight('bold').setFontSize(11).setHorizontalAlignment('center').setVerticalAlignment('middle');
  for(let c=1;c<=maxCols;c++) sheet.setColumnWidth(c,c===1?155:185);
  sheet.getRange(1,1,Math.max(sheet.getMaxRows(),2),maxCols).setVerticalAlignment('middle');
}
