const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const scripts = ['automation_hub.gs', 'vehicle_event_trigger.gs', 'report_branding.gs'];
const source = scripts.map(file => fs.readFileSync(path.join(__dirname, '../apps-script', file), 'utf8')).join('\n');
assert.equal([...source.matchAll(/function\s+doPost\s*\(/g)].length, 1, 'the deployed project must have one POST entry point');
const context = {
  PropertiesService: {getScriptProperties: () => ({getProperty: () => 'vehicle-key'})},
  ContentService: {MimeType: {JSON: 'json'}, createTextOutput: text => ({setMimeType: () => JSON.parse(text)})},
};
vm.createContext(context);
vm.runInContext(source, context);
let callbacks = 0;
context.hubReportCallback_ = event => {callbacks++; return {route: 'hub', event};};
const callback = {postData: {contents: '{}'}};
assert.equal(context.doPost(callback).route, 'hub');
assert.equal(callbacks, 1);
assert.equal(context.doPost({parameter: {key: 'wrong'}, postData: {contents: '{}'}}).error, 'Unauthorized');
assert.equal(callbacks, 1, 'invalid vehicle keys cannot fall back to report callback');
assert.equal(context.doPost({parameter: {key: 'vehicle-key'}, postData: {contents: '{}'}}).error, 'Depot is missing.');
assert.equal(callbacks, 1, 'valid vehicle keys retain the existing vehicle validation path');
console.log('Single POST entry point, Hub routing, and vehicle-key isolation passed');

let cleared = 0;
const cell = {
  getDisplayValues: () => [['Automation Status', 'Drive Report Link']],
  setValue: () => {}, clearContent: () => {cleared++;},
};
const sheet = {getLastColumn: () => 2, getRange: () => cell};
context.hubStatus_(sheet, 21, 'SUBMITTED | DAILY | PRODDUTUR | 2026-10-03');
assert.equal(cleared, 1, 'new requests must clear inherited links');
context.hubStatus_(sheet, 21, 'COMPLETED | DAILY | PRODDUTUR | 2026-10-02');
assert.equal(cleared, 1, 'completion must preserve the authenticated callback link');
console.log('Submitted-row stale link removal and completed-link preservation passed');
