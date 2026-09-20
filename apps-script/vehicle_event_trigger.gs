/* APSRTC – PRODDUTUR VEHICLE EVENT REGISTER
 * Google Form -> Google Sheet permanent register -> GitHub workflow dispatch
 * Script Property required: GITHUB_TOKEN
 */

const CONFIG = {
  SHEET_NAME: 'Vehicle Events',
  DEPOT: 'PRODDUTUR',
  DEPOT_CODE: 'PDT',
  TIMEZONE: 'Asia/Kolkata',
  GITHUB_REPO: 'imranshaik-pro/apsrtc-kmpl',
  GITHUB_WORKFLOW: 'vehicle-event.yml',
  GITHUB_BRANCH: 'master'
};

function onVehicleEventSubmit(e) {
  if (!e || !e.range) {
    throw new Error('This function must run from the spreadsheet Form Submit trigger.');
  }

  const sheet = e.range.getSheet();
  if (sheet.getName() !== CONFIG.SHEET_NAME) return;

  const row = e.range.getRow();

  try {
    const data = readSubmittedRow_(sheet, row);

    const eventDateRaw = getFirstValue_(data, ['Event Date']);
    const vehicleNo = normalizeVehicle_(getFirstValue_(data, ['Vehicle No']));
    const eventType = normalizeEventType_(getFirstValue_(data, ['Event Type']));
    const components = splitCheckbox_(getFirstValue_(data, ['Component/Aggregate']));
    const springPositions = splitCheckbox_(getFirstValue_(data, ['Spring Assembly Change Position']));
    const tyrePositions = splitCheckbox_(getFirstValue_(data, ['Tyres Change Position', 'TYRE CHANGE']));
    const breakdownLocation = getFirstValue_(data, ['Break Down Location']);
    const kmsCancelled = getFirstValue_(data, ['KMs Canceled']);
    const breakdownDetails = getFirstValue_(data, ['Break Down Details']);
    const remarks = getFirstValue_(data, ['Remarks']);

    if (!eventDateRaw) throw new Error('Event Date is missing.');
    if (!vehicleNo) throw new Error('Vehicle No is missing.');
    if (!eventType) throw new Error('Event Type is missing.');

    const allowedTypes = [
      'UNIT CHANGE',
      'BREAKDOWN',
      'TYRE CHANGE',
      'SCHEDULE III',
      'SCHEDULE IV'
    ];
    if (!allowedTypes.includes(eventType)) {
      throw new Error('Unsupported Event Type: ' + eventType);
    }

    const tyreNumbers = {
      FOS: getFirstNonBlankValue_(data, ['FOS Tyre No', 'FOS Tyre NO']),
      FNS: getFirstNonBlankValue_(data, ['FNS Tyre No']),
      ROSO: getFirstNonBlankValue_(data, ['ROSO Tyre No']),
      ROSI: getFirstNonBlankValue_(data, ['ROSI Tyre No']),
      RNSO: getFirstNonBlankValue_(data, ['RNSO Tyre No']),
      RNSI: getFirstNonBlankValue_(data, ['RNSI Tyre No']),
      SPARE: getFirstNonBlankValue_(data, ['Spare Tyre No'])
    };

    const tyrePositionMap = {
      'FOS': 'FOS', 'FOS TYRE NO': 'FOS',
      'FNS': 'FNS', 'FNS TYRE NO': 'FNS',
      'ROSO': 'ROSO', 'ROSO TYRE NO': 'ROSO',
      'ROSI': 'ROSI', 'ROSI TYRE NO': 'ROSI',
      'RNSO': 'RNSO', 'RNSO TYRE NO': 'RNSO',
      'RNSI': 'RNSI', 'RNSI TYRE NO': 'RNSI',
      'SPARE': 'SPARE', 'SPARE TYRE NO': 'SPARE'
    };

    const tyreHistory = [];
    tyrePositions.forEach(rawPosition => {
      const key = String(rawPosition || '').trim().toUpperCase().replace(/\s+/g, ' ');
      const position = tyrePositionMap[key];
      if (!position) throw new Error('Unknown tyre position: ' + rawPosition);
      const tyreNo = String(tyreNumbers[position] || '').trim();
      tyreHistory.push(tyreNo ? position + ': ' + tyreNo : position + ': TYRE NO NOT ENTERED');
    });

    const eventDate = parseEventDate_(eventDateRaw);
    if (!eventDate) throw new Error('Unable to interpret Event Date: ' + eventDateRaw);

    const eventDateISO = Utilities.formatDate(eventDate, CONFIG.TIMEZONE, 'yyyy-MM-dd');
    const createdAt = Utilities.formatDate(new Date(), CONFIG.TIMEZONE, 'yyyy-MM-dd HH:mm:ss');
    const eventId = makeEventId_(eventDate, vehicleNo, row);

    setAuditValue_(sheet, row, 'Event ID', eventId);
    setAuditValue_(sheet, row, 'Depot', CONFIG.DEPOT);
    setAuditValue_(sheet, row, 'Created At', createdAt);
    setAuditValue_(sheet, row, 'Entry Source', 'GOOGLE_FORM');
    setAuditValue_(sheet, row, 'Normalized Event Date', eventDateISO);
    setAuditValue_(sheet, row, 'Normalized Vehicle No', vehicleNo);
    setAuditValue_(sheet, row, 'Normalized Event Type', eventType);
    setAuditValue_(sheet, row, 'Components', components.join(' | '));
    setAuditValue_(sheet, row, 'Spring Positions', springPositions.join(' | '));
    setAuditValue_(sheet, row, 'Tyre History', tyreHistory.join(' | '));
    setAuditValue_(sheet, row, 'Breakdown Location', breakdownLocation);
    setAuditValue_(sheet, row, 'KM Cancelled', kmsCancelled);
    setAuditValue_(sheet, row, 'Breakdown Details', breakdownDetails);
    setAuditValue_(sheet, row, 'Event Remarks', remarks);
    setAuditValue_(sheet, row, 'Automation Status', 'EVENT RECORDED');

    dispatchToGitHub_({
      event_id: eventId,
      created_at: createdAt,
      event_date: eventDateISO,
      depot: CONFIG.DEPOT,
      vehicle_no: vehicleNo,
      event_type: eventType,
      components: components.join(' | '),
      spring_positions: springPositions.join(' | '),
      tyre_history: tyreHistory.join(' | '),
      breakdown_location: breakdownLocation,
      kms_cancelled: String(kmsCancelled || ''),
      breakdown_details: breakdownDetails,
      remarks: remarks,
      entry_source: 'GOOGLE_FORM'
    });

    setAuditValue_(sheet, row, 'GitHub Dispatch Status', 'DISPATCHED');

    console.log(JSON.stringify({
      eventId: eventId,
      eventDate: eventDateISO,
      vehicleNo: vehicleNo,
      eventType: eventType,
      tyreHistory: tyreHistory,
      github: 'DISPATCHED'
    }));

  } catch (error) {
    setAuditValue_(sheet, row, 'Automation Status', 'ERROR: ' + error.message);
    setAuditValue_(sheet, row, 'GitHub Dispatch Status', 'ERROR: ' + error.message);
    console.error(error);
    throw error;
  }
}

function dispatchToGitHub_(inputs) {
  const token = PropertiesService.getScriptProperties().getProperty('GITHUB_TOKEN');
  if (!token) throw new Error('GITHUB_TOKEN is missing from Script Properties.');

  const url =
    'https://api.github.com/repos/' + CONFIG.GITHUB_REPO +
    '/actions/workflows/' + CONFIG.GITHUB_WORKFLOW + '/dispatches';

  const response = UrlFetchApp.fetch(url, {
    method: 'post',
    contentType: 'application/json',
    headers: {
      Authorization: 'Bearer ' + token,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28'
    },
    payload: JSON.stringify({
      ref: CONFIG.GITHUB_BRANCH,
      inputs: inputs
    }),
    muteHttpExceptions: true
  });

  const code = response.getResponseCode();
  if (code !== 204) {
    throw new Error('GitHub dispatch failed (' + code + '): ' + response.getContentText());
  }
}

function readSubmittedRow_(sheet, row) {
  const lastColumn = sheet.getLastColumn();
  const headers = sheet.getRange(1, 1, 1, lastColumn).getDisplayValues()[0];
  const values = sheet.getRange(row, 1, 1, lastColumn).getDisplayValues()[0];
  const data = {};

  headers.forEach((header, index) => {
    const key = String(header || '').trim();
    if (!key) return;
    if (!data[key]) data[key] = [];
    data[key].push(String(values[index] || '').trim());
  });
  return data;
}

function getFirstValue_(data, possibleHeaders) {
  for (const header of possibleHeaders) {
    const values = data[header];
    if (Array.isArray(values) && values.length) return String(values[0] || '').trim();
  }
  return '';
}

function getFirstNonBlankValue_(data, possibleHeaders) {
  for (const header of possibleHeaders) {
    const values = data[header];
    if (!Array.isArray(values)) continue;
    for (const value of values) {
      const cleaned = String(value || '').trim();
      if (cleaned) return cleaned;
    }
  }
  return '';
}

function splitCheckbox_(value) {
  if (!value) return [];
  return String(value).split(',').map(v => v.trim()).filter(Boolean);
}

function normalizeVehicle_(value) {
  return String(value || '').trim().toUpperCase().replace(/\s+/g, '');
}

function normalizeEventType_(value) {
  const raw = String(value || '').trim().toUpperCase().replace(/\s+/g, ' ');
  const aliases = {
    'UNIT': 'UNIT CHANGE',
    'UNIT CHANGE': 'UNIT CHANGE',
    'BREAK DOWN': 'BREAKDOWN',
    'BREAKDOWN': 'BREAKDOWN',
    'TYRE': 'TYRE CHANGE',
    'TYRES': 'TYRE CHANGE',
    'TYRE CHANGE': 'TYRE CHANGE',
    'TYRES CHANGE': 'TYRE CHANGE',
    'SCHEDULE III': 'SCHEDULE III',
    'SCHEDULE 3': 'SCHEDULE III',
    'SCHEDULE IV': 'SCHEDULE IV',
    'SCHEDULE 4': 'SCHEDULE IV'
  };
  return aliases[raw] || raw;
}

function parseEventDate_(value) {
  if (value instanceof Date) return value;
  const text = String(value || '').trim();
  if (!text) return null;

  let match = text.match(/^(\d{4})-(\d{1,2})-(\d{1,2})$/);
  if (match) return new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]));

  match = text.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
  if (match) return new Date(Number(match[3]), Number(match[1]) - 1, Number(match[2]));

  const parsed = new Date(text);
  return isNaN(parsed.getTime()) ? null : parsed;
}

function makeEventId_(eventDate, vehicleNo, row) {
  const datePart = Utilities.formatDate(eventDate, CONFIG.TIMEZONE, 'yyyyMMdd');
  const timePart = Utilities.formatDate(new Date(), CONFIG.TIMEZONE, 'HHmmss');
  const rowPart = 'R' + String(row).padStart(4, '0');
  return [CONFIG.DEPOT_CODE, datePart, vehicleNo, rowPart, timePart].join('-');
}

function setAuditValue_(sheet, row, header, value) {
  const lastColumn = sheet.getLastColumn();
  const headers = sheet.getRange(1, 1, 1, lastColumn).getDisplayValues()[0];
  let column = headers.indexOf(header) + 1;

  if (column === 0) {
    column = lastColumn + 1;
    sheet.getRange(1, column).setValue(header).setFontWeight('bold');
  }
  sheet.getRange(row, column).setValue(value);
}

function setupVehicleEventTrigger() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  ScriptApp.getProjectTriggers().forEach(trigger => {
    if (trigger.getHandlerFunction() === 'onVehicleEventSubmit') {
      ScriptApp.deleteTrigger(trigger);
    }
  });

  ScriptApp.newTrigger('onVehicleEventSubmit')
    .forSpreadsheet(spreadsheet)
    .onFormSubmit()
    .create();

  console.log('Vehicle Event Form trigger installed successfully.');
}
