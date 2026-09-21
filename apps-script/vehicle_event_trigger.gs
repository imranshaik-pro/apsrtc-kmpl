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
    const selectedDepot = String(getFirstNonBlankValue_(data, ['Depot']) || CONFIG.DEPOT).trim().toUpperCase();

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
    setAuditValue_(sheet, row, 'Depot', selectedDepot);
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
      depot: selectedDepot,
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
    const message = String(error && error.message ? error.message : error);
    // Preserve the permanent-record state if the sheet write succeeded.
    // A later GitHub dispatch failure must not falsely label the recorded event itself as invalid.
    let recorded = false;
    try {
      const current = readSubmittedRow_(sheet, row);
      recorded = getFirstNonBlankValue_(current, ['Automation Status']) === 'EVENT RECORDED';
    } catch (ignore) {
      recorded = false;
    }

    if (!recorded) {
      setAuditValue_(sheet, row, 'Automation Status', 'ERROR: ' + message);
    }
    setAuditValue_(sheet, row, 'GitHub Dispatch Status', 'ERROR: ' + message);
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
  const vehicle = String(value || '').trim().toUpperCase().replace(/\s+/g, '');
  return vehicle.startsWith('AP') ? vehicle.substring(2) : vehicle;
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

/**
 * One-time bootstrap: copy the existing Depot choices from the linked Google
 * Form into the "Depot Master" sheet. This preserves the list already entered
 * by the operator and avoids retyping it.
 */
function importDepotMasterFromForm() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const master = ss.getSheetByName('Depot Master');
  if (!master) throw new Error('Depot Master sheet not found.');

  const formUrl = ss.getFormUrl();
  if (!formUrl) throw new Error('This spreadsheet is not linked to a Google Form.');
  const form = FormApp.openByUrl(formUrl);
  const item = findDepotItem_(form);
  const depots = getDepotChoices_(item);
  if (!depots.length) throw new Error('The Depot question has no choices.');

  master.getRange(1, 1).setValue('Depot').setFontWeight('bold');
  if (master.getMaxRows() > 1) {
    master.getRange(2, 1, master.getMaxRows() - 1, 1).clearContent();
  }
  master.getRange(2, 1, depots.length, 1).setValues(depots.map(d => [d]));
  console.log('DEPOT_MASTER_IMPORTED: ' + depots.length + ' depots');
}

/**
 * Push Depot Master values back into this spreadsheet's linked Vehicle Event
 * Form. Run this after adding/renaming/removing a depot in Depot Master.
 */
function syncDepotMasterToVehicleEventForm() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const master = ss.getSheetByName('Depot Master');
  if (!master) throw new Error('Depot Master sheet not found.');
  const lastRow = master.getLastRow();
  if (lastRow < 2) throw new Error('Depot Master is empty.');

  const depots = master.getRange(2, 1, lastRow - 1, 1).getDisplayValues()
    .flat().map(v => String(v || '').trim().toUpperCase()).filter(Boolean);
  const unique = [...new Set(depots)];
  if (!unique.length) throw new Error('Depot Master is empty.');

  const formUrl = ss.getFormUrl();
  if (!formUrl) throw new Error('This spreadsheet is not linked to a Google Form.');
  const form = FormApp.openByUrl(formUrl);
  const item = findDepotItem_(form);
  setDepotChoices_(item, unique);
  console.log('DEPOT_FORM_SYNCED: ' + unique.length + ' depots');
}

function findDepotItem_(form) {
  const item = form.getItems().find(i => String(i.getTitle() || '').trim().toUpperCase() === 'DEPOT');
  if (!item) throw new Error('Required Form question "Depot" was not found.');
  return item;
}

function getDepotChoices_(item) {
  const type = item.getType();
  if (type === FormApp.ItemType.LIST) {
    return item.asListItem().getChoices().map(c => c.getValue()).map(v => String(v).trim()).filter(Boolean);
  }
  if (type === FormApp.ItemType.MULTIPLE_CHOICE) {
    return item.asMultipleChoiceItem().getChoices().map(c => c.getValue()).map(v => String(v).trim()).filter(Boolean);
  }
  throw new Error('Depot must be a Dropdown or Multiple choice question.');
}

function setDepotChoices_(item, depots) {
  const type = item.getType();
  if (type === FormApp.ItemType.LIST) {
    item.asListItem().setChoiceValues(depots).setRequired(true);
    return;
  }
  if (type === FormApp.ItemType.MULTIPLE_CHOICE) {
    item.asMultipleChoiceItem().setChoiceValues(depots).setRequired(true);
    return;
  }
  throw new Error('Depot must be a Dropdown or Multiple choice question.');
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


/**
 * Read-only Vehicle Events API for Vehicle 360.
 *
 * Deploy this Apps Script as a Web App. Requests must provide the API key in
 * the query string: ?key=<VEHICLE_EVENTS_API_KEY>
 *
 * The API returns only normalized audit fields from the permanent Vehicle
 * Events sheet. The Google Sheet remains the source of truth.
 */
function doGet(e) {
  try {
    // Keep the Web API self-contained. The deployed Web App must not depend
    // on the trigger CONFIG object being visible in its execution context.
    const SHEET_NAME = 'Vehicle Events';
    const DEPOT_NAME = 'PRODDUTUR';

    const expectedKey = PropertiesService.getScriptProperties().getProperty('VEHICLE_EVENTS_API_KEY');
    const suppliedKey = e && e.parameter ? String(e.parameter.key || '').trim() : '';

    if (!expectedKey) {
      return jsonResponse_({ok: false, error: 'VEHICLE_EVENTS_API_KEY is not configured.'});
    }
    if (!suppliedKey || suppliedKey !== expectedKey) {
      return jsonResponse_({ok: false, error: 'Unauthorized'});
    }

    const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
    if (!spreadsheet) {
      return jsonResponse_({ok: false, error: 'Unable to access active spreadsheet.'});
    }
    const sheet = spreadsheet.getSheetByName(SHEET_NAME);
    if (!sheet) {
      return jsonResponse_({ok: false, error: 'Vehicle Events sheet not found.'});
    }

    const values = sheet.getDataRange().getDisplayValues();
    if (values.length < 2) {
      return jsonResponse_({ok: true, depot: DEPOT_NAME, count: 0, events: []});
    }

    const headers = values[0].map(v => String(v || '').trim());
    const index = {};
    headers.forEach((header, i) => {
      if (header && index[header] === undefined) index[header] = i;
    });
    const get = (row, header) =>
      index[header] === undefined ? '' : String(row[index[header]] || '').trim();

    const events = values.slice(1).map(row => {
      const vehicleNo = normalizeVehicle_(
        get(row, 'Normalized Vehicle No') || get(row, 'Vehicle No')
      );
      const eventType = normalizeEventType_(
        get(row, 'Normalized Event Type') || get(row, 'Event Type')
      );
      return {
        event_id: get(row, 'Event ID'),
        created_at: get(row, 'Created At'),
        event_date: get(row, 'Normalized Event Date') || get(row, 'Event Date'),
        depot: get(row, 'Depot') || DEPOT_NAME,
        vehicle_no: vehicleNo,
        event_type: eventType,
        components: get(row, 'Components'),
        spring_positions: get(row, 'Spring Positions'),
        tyre_history: get(row, 'Tyre History'),
        breakdown_location: get(row, 'Breakdown Location'),
        kms_cancelled: get(row, 'KM Cancelled'),
        breakdown_details: get(row, 'Breakdown Details'),
        remarks: get(row, 'Event Remarks') || get(row, 'Remarks'),
        entry_source: get(row, 'Entry Source') || 'GOOGLE_FORM'
      };
    }).filter(event =>
      event.event_id &&
      event.event_date &&
      event.vehicle_no &&
      event.event_type
    );

    return jsonResponse_({
      ok: true,
      depot: DEPOT_NAME,
      count: events.length,
      events: events
    });
  } catch (error) {
    return jsonResponse_({ok: false, error: String(error && error.message ? error.message : error)});
  }
}

/**
 * Authorized write API used by the Telegram guided Vehicle Event flow.
 * The permanent Google Sheet remains the source of truth.
 */
function doPost(e) {
  try {
    const expectedKey = PropertiesService.getScriptProperties().getProperty('VEHICLE_EVENTS_API_KEY');
    const suppliedKey = e && e.parameter ? String(e.parameter.key || '').trim() : '';
    if (!expectedKey || suppliedKey !== expectedKey) return jsonResponse_({ok:false,error:'Unauthorized'});

    const payload = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    const depot = String(payload.depot || '').trim().toUpperCase();
    const vehicleNo = normalizeVehicle_(payload.vehicle_no);
    const eventType = normalizeEventType_(payload.event_type);
    const eventDate = parseEventDate_(payload.event_date);
    const allowedTypes = ['UNIT CHANGE','BREAKDOWN','TYRE CHANGE','SCHEDULE III','SCHEDULE IV'];
    if (!depot) throw new Error('Depot is missing.');
    if (!vehicleNo) throw new Error('Vehicle No is missing.');
    if (!eventDate) throw new Error('Event Date is invalid.');
    if (!allowedTypes.includes(eventType)) throw new Error('Unsupported Event Type: ' + eventType);

    const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = spreadsheet.getSheetByName('Vehicle Events');
    if (!sheet) throw new Error('Vehicle Events sheet not found.');
    const row = sheet.getLastRow() + 1;
    const createdAt = Utilities.formatDate(new Date(), CONFIG.TIMEZONE, 'yyyy-MM-dd HH:mm:ss');
    const eventDateISO = Utilities.formatDate(eventDate, CONFIG.TIMEZONE, 'yyyy-MM-dd');
    const depotCode = depot.replace(/[^A-Z0-9]/g, '').substring(0, 3) || 'DEP';
    const eventId = [depotCode, Utilities.formatDate(eventDate, CONFIG.TIMEZONE, 'yyyyMMdd'),
      vehicleNo, 'R' + String(row).padStart(4,'0'), Utilities.formatDate(new Date(), CONFIG.TIMEZONE, 'HHmmss')].join('-');

    const fields = {
      'Event ID': eventId, 'Depot': depot, 'Created At': createdAt, 'Entry Source': 'TELEGRAM',
      'Normalized Event Date': eventDateISO, 'Normalized Vehicle No': vehicleNo,
      'Normalized Event Type': eventType, 'Components': String(payload.components || ''),
      'Spring Positions': String(payload.spring_positions || ''), 'Tyre History': String(payload.tyre_history || ''),
      'Breakdown Location': String(payload.breakdown_location || ''), 'KM Cancelled': String(payload.kms_cancelled || ''),
      'Breakdown Details': String(payload.breakdown_details || ''), 'Event Remarks': String(payload.remarks || ''),
      'Automation Status': 'EVENT RECORDED'
    };
    Object.keys(fields).forEach(header => setAuditValue_(sheet,row,header,fields[header]));

    dispatchToGitHub_({
      event_id:eventId, created_at:createdAt, event_date:eventDateISO, depot:depot,
      vehicle_no:vehicleNo, event_type:eventType, components:fields['Components'],
      spring_positions:fields['Spring Positions'], tyre_history:fields['Tyre History'],
      breakdown_location:fields['Breakdown Location'], kms_cancelled:fields['KM Cancelled'],
      breakdown_details:fields['Breakdown Details'], remarks:fields['Event Remarks'], entry_source:'TELEGRAM'
    });
    setAuditValue_(sheet,row,'GitHub Dispatch Status','DISPATCHED');
    return jsonResponse_({ok:true,event_id:eventId,row:row});
  } catch (error) {
    return jsonResponse_({ok:false,error:String(error && error.message ? error.message : error)});
  }
}

function jsonResponse_(payload) {
  return ContentService
    .createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * Run once if VEHICLE_EVENTS_API_KEY does not yet exist.
 * It creates a random UUID in Script Properties without hard-coding it.
 */
function setupVehicleEventsApiKey() {
  const props = PropertiesService.getScriptProperties();
  if (!props.getProperty('VEHICLE_EVENTS_API_KEY')) {
    props.setProperty('VEHICLE_EVENTS_API_KEY', Utilities.getUuid());
  }
  console.log('VEHICLE_EVENTS_API_KEY is configured in Script Properties.');
}
