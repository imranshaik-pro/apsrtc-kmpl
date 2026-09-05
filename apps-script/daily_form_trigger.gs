/* APSRTC Daily Report - Google Form / Response Sheet trigger
 * Bind this script to the DAILY response spreadsheet.
 * Script Property required: GITHUB_TOKEN
 */

const REPO = 'imranshaik-pro/apsrtc-kmpl';
const WORKFLOW = 'daily-report.yml';
const BRANCH = 'master';
const TZ = 'Asia/Kolkata';

function onFormSubmit(e) {
  const sheet = e.range.getSheet();
  const row = e.range.getRow();
  const named = e.namedValues || {};

  try {
    const depot = pickValue_(named, ['depot']);
    const rawDate = pickValue_(named, ['date']);
    if (!depot) throw new Error('Depot was not found in the form response.');
    if (!rawDate) throw new Error('Date was not found in the form response.');

    const reportDate = normalizeDate_(rawDate);
    const today = Utilities.formatDate(new Date(), TZ, 'yyyy-MM-dd');
    if (reportDate > today) {
      setStatus_(sheet, row, "LOL! Can't retrieve future-date data.");
      return;
    }

    dispatch_(WORKFLOW, {
      depot: depot,
      report_date: reportDate
    });
    setStatus_(sheet, row, 'Submitted to GitHub');
  } catch (err) {
    setStatus_(sheet, row, 'ERROR: ' + err.message);
    throw err;
  }
}

function setupDailyTrigger() {
  deleteTriggers_('onFormSubmit');
  ScriptApp.newTrigger('onFormSubmit')
    .forSpreadsheet(SpreadsheetApp.getActive())
    .onFormSubmit()
    .create();
}

function dispatch_(workflow, inputs) {
  const token = PropertiesService.getScriptProperties().getProperty('GITHUB_TOKEN');
  if (!token) throw new Error('GITHUB_TOKEN is missing from Script Properties.');

  const url = `https://api.github.com/repos/${REPO}/actions/workflows/${workflow}/dispatches`;
  const response = UrlFetchApp.fetch(url, {
    method: 'post',
    contentType: 'application/json',
    headers: {
      Authorization: 'Bearer ' + token,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28'
    },
    payload: JSON.stringify({ ref: BRANCH, inputs: inputs }),
    muteHttpExceptions: true
  });

  if (response.getResponseCode() !== 204) {
    throw new Error(`GitHub dispatch failed (${response.getResponseCode()}): ${response.getContentText()}`);
  }
}

function pickValue_(named, keywords) {
  const keys = Object.keys(named);
  for (const keyword of keywords) {
    const match = keys.find(k => k.toLowerCase().includes(keyword));
    if (match) {
      const value = named[match];
      return Array.isArray(value) ? String(value[0]).trim() : String(value).trim();
    }
  }
  return '';
}

function normalizeDate_(raw) {
  raw = String(raw).trim();
  let m = raw.match(/^(\d{4})-(\d{1,2})-(\d{1,2})$/);
  if (m) return `${m[1]}-${pad2_(m[2])}-${pad2_(m[3])}`;

  m = raw.match(/^(\d{1,2})[\/-](\d{1,2})[\/-](\d{4})$/);
  if (m) return `${m[3]}-${pad2_(m[2])}-${pad2_(m[1])}`; // India: DD/MM/YYYY

  const d = new Date(raw);
  if (isNaN(d.getTime())) throw new Error('Invalid date: ' + raw);
  return Utilities.formatDate(d, TZ, 'yyyy-MM-dd');
}

function setStatus_(sheet, row, status) {
  const headerRow = 1;
  const values = sheet.getRange(headerRow, 1, 1, sheet.getLastColumn()).getValues()[0];
  let col = values.findIndex(v => String(v).trim() === 'Automation Status') + 1;
  if (!col) {
    col = sheet.getLastColumn() + 1;
    sheet.getRange(headerRow, col).setValue('Automation Status');
  }
  sheet.getRange(row, col).setValue(status);
}

function deleteTriggers_(handler) {
  ScriptApp.getProjectTriggers().forEach(t => {
    if (t.getHandlerFunction() === handler) ScriptApp.deleteTrigger(t);
  });
}

function pad2_(v) {
  return String(v).padStart(2, '0');
}
