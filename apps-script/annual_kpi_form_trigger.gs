/* APSRTC Annual KPI - Google Form / Response Sheet trigger
 * Bind this script to the ANNUAL KPI response spreadsheet.
 * Script Property required: GITHUB_TOKEN
 */

const REPO = 'imranshaik-pro/apsrtc-kmpl';
const WORKFLOW = 'annual-kpi.yml';
const BRANCH = 'master';
const DEFAULT_FYS = '2023-24,2024-25,2025-26';

function onFormSubmit(e) {
  const sheet = e.range.getSheet();
  const row = e.range.getRow();
  const named = e.namedValues || {};

  try {
    const depot = pickValue_(named, ['depot']);
    if (!depot) throw new Error('Depot was not found in the form response.');

    let fys = pickValue_(named, ['financial year', 'financial_year', 'fy', 'year']);
    if (!fys) fys = DEFAULT_FYS;
    fys = normalizeFYs_(fys);

    dispatch_(WORKFLOW, {
      depot: depot,
      financial_years: fys
    });
    setStatus_(sheet, row, 'Submitted to GitHub');
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

function normalizeFYs_(raw) {
  const parts = String(raw).split(/[,;\n]+/).map(s => s.trim()).filter(Boolean);
  const normalized = parts.map(normalizeFY_);
  return [...new Set(normalized)].join(',');
}

function normalizeFY_(raw) {
  raw = String(raw).trim();
  let m = raw.match(/^(20\d{2})\s*[-/]\s*(\d{2})$/);
  if (m) {
    const expected = String(Number(m[1]) + 1).slice(-2);
    if (m[2] !== expected) throw new Error('Invalid financial year: ' + raw);
    return m[1] + '-' + m[2];
  }
  m = raw.match(/^(20\d{2})\s*[-/]\s*(20\d{2})$/);
  if (m && Number(m[2]) === Number(m[1]) + 1) {
    return m[1] + '-' + m[2].slice(-2);
  }
  throw new Error('Financial year must be like 2025-26.');
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
