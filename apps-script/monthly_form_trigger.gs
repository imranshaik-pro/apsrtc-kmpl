/* APSRTC Monthly Report - Google Form / Response Sheet trigger
 * Bind this script to the MONTHLY response spreadsheet.
 * Script Property required: GITHUB_TOKEN
 */

const REPO = 'imranshaik-pro/apsrtc-kmpl';
const WORKFLOW = 'monthly-report.yml';
const BRANCH = 'master';
const TZ = 'Asia/Kolkata';

function onFormSubmit(e) {
  const sheet = e.range.getSheet();
  const row = e.range.getRow();
  const named = e.namedValues || {};

  try {
    const depot = pickValue_(named, ['Depot']);
    const rawMonth = pickValue_(named, ['Month', 'Report Month', 'Date']);
    if (!depot) throw new Error('Depot was not found in the form response.');
    if (!rawMonth) throw new Error('Month/date was not found in the form response.');

    const month = normalizeMonth_(rawMonth);
    const currentMonth = Utilities.formatDate(new Date(), TZ, 'yyyy-MM');
    if (month > currentMonth) {
      setStatus_(sheet, row, "LOL! Can't retrieve future-month data.");
      return;
    }

    dispatch_(WORKFLOW, {
      depot: depot,
      month: month
    });
    setStatus_(sheet, row, 'Submitted to GitHub');
  } catch (err) {
    setStatus_(sheet, row, 'ERROR: ' + err.message);
    throw err;
  }
}

function setupMonthlyTrigger() {
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

function pickValue_(named, candidateHeaders) {
  // Match form headers deliberately: exact normalized header first, then
  // normalized whole-header fallback. Avoid broad substring matching such as
  // "date" matching "Created Date" or "month" matching another field.
  const normalizeHeader = value => String(value || '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  const entries = Object.keys(named).map(key => ({
    key: key,
    normalized: normalizeHeader(key)
  }));

  for (const candidate of candidateHeaders) {
    const target = normalizeHeader(candidate);
    const match = entries.find(entry => entry.normalized === target);
    if (match) {
      const value = named[match.key];
      return Array.isArray(value) ? String(value[0] || '').trim() : String(value || '').trim();
    }
  }
  return '';
}

function normalizeMonth_(raw) {
  raw = String(raw).trim();
  let m = raw.match(/^(\d{4})-(\d{1,2})$/);
  if (m) return `${m[1]}-${pad2_(m[2])}`;

  m = raw.match(/^(\d{4})-(\d{1,2})-(\d{1,2})$/);
  if (m) return `${m[1]}-${pad2_(m[2])}`;

  m = raw.match(/^(\d{1,2})[\/-](\d{1,2})[\/-](\d{4})$/);
  if (m) return `${m[3]}-${pad2_(m[2])}`; // India: DD/MM/YYYY

  m = raw.match(/^(\d{1,2})[\/-](\d{4})$/);
  if (m) return `${m[2]}-${pad2_(m[1])}`; // MM/YYYY

  const d = new Date(raw);
  if (isNaN(d.getTime())) throw new Error('Invalid month/date: ' + raw);
  return Utilities.formatDate(d, TZ, 'yyyy-MM');
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
