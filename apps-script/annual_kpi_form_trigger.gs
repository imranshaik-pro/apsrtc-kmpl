/* APSRTC Annual KPI - Google Form / Response Sheet trigger
 * Form inputs: Depot + Month only.
 * Bind this script to the ANNUAL KPI response spreadsheet.
 * Script Property required: GITHUB_TOKEN
 */

const REPO = 'imranshaik-pro/apsrtc-kmpl';
const WORKFLOW = 'annual-kpi.yml';
const BRANCH = 'master';

function onFormSubmit(e) {
  const sheet = e.range.getSheet();
  const row = e.range.getRow();
  const named = e.namedValues || {};

  try {
    const depot = pickValue_(named, ['depot']);
    if (!depot) throw new Error('Depot was not found in the form response.');

    const rawMonth = pickValue_(named, ['month']);
    if (!rawMonth) throw new Error('Month was not found in the form response.');

    const selectedMonth = normalizeMonth_(rawMonth);
    const fy = financialYearForMonth_(selectedMonth);

    dispatch_(WORKFLOW, {
      depot: depot,
      selected_month: selectedMonth,
      financial_years: fy
    });
    setStatus_(sheet, row, `Submitted to GitHub | ${selectedMonth} | FY ${fy}`);
  } catch (err) {
    setStatus_(sheet, row, 'ERROR: ' + err.message);
    throw err;
  }
}

function setupAnnualKpiTrigger() {
  deleteTriggers_('onFormSubmit');
  ScriptApp.newTrigger('onFormSubmit')
    .forSpreadsheet(SpreadsheetApp.getActive())
    .onFormSubmit()
    .create();
}

function normalizeMonth_(raw) {
  const text = String(raw).trim();
  let m = text.match(/^(20\d{2})[-\/]([01]?\d)$/);
  if (m) {
    const month = Number(m[2]);
    if (month >= 1 && month <= 12) return `${m[1]}-${String(month).padStart(2, '0')}`;
  }
  m = text.match(/^([A-Za-z]{3,9})[\s\-\/]+(20\d{2})$/);
  if (m) {
    const names = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'];
    const idx = names.indexOf(m[1].slice(0,3).toLowerCase());
    if (idx >= 0) return `${m[2]}-${String(idx + 1).padStart(2, '0')}`;
  }
  m = text.match(/^([01]?\d)[\s\-\/]+(20\d{2})$/);
  if (m) {
    const month = Number(m[1]);
    if (month >= 1 && month <= 12) return `${m[2]}-${String(month).padStart(2, '0')}`;
  }
  throw new Error('Month must identify a month and year, for example Aug 2026 or 2026-08. Received: ' + text);
}

function financialYearForMonth_(yyyyMm) {
  const parts = yyyyMm.split('-');
  const year = Number(parts[0]);
  const month = Number(parts[1]);
  const start = month >= 4 ? year : year - 1;
  return `${start}-${String(start + 1).slice(-2)}`;
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
