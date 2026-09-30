// Run: node tests/test_hub_dispatch.cjs [workflow-contracts.json]
// The JSON maps workflow filenames to their declared dispatch input names.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const contracts = process.argv[2] ? JSON.parse(fs.readFileSync(process.argv[2], 'utf8')) :
  Object.fromEntries(['annual-kpi.yml', 'monthly-report.yml', 'daily-report.yml'].map(name => {
    const yaml = fs.readFileSync(path.join(__dirname, '../.github/workflows', name), 'utf8');
    const dispatch = yaml.split('  workflow_dispatch:')[1].split(/^\S/m)[0];
    return [name, [...dispatch.matchAll(/^      ([a-z_]+):$/gm)].map(match => match[1])];
  }));
const ctx = {Utilities: {formatDate: () => '2026-09-30'}};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(__dirname, '../apps-script/automation_hub.gs'), 'utf8'), ctx);
const calls = [];
ctx.hubDispatch_ = (workflow, inputs) => calls.push({workflow, inputs});
ctx.hubStatus_ = () => {};
for (const depot of ['PRODDUTUR', 'RAJAMPET']) {
  for (const month of ['5/1/2026', '7/1/2026', '5/1/2026']) {
    for (const service of ['Annual KPI Report', 'Monthly Performance Report']) {
      const annual = service.startsWith('Annual');
      const namedValues = {Depot: [depot], 'Required Service / Report': [service],
        'Selected Month': [annual ? month : ''], 'Report Month': [annual ? '' : month]};
      ctx.onHubSubmit({namedValues, range: {getSheet: () => ({}), getRow: () => 12}});
      const {workflow, inputs} = calls.at(-1);
      assert.equal(workflow, annual ? 'annual-kpi.yml' : 'monthly-report.yml');
      assert.equal(inputs.depot, depot);
      assert.equal(inputs.hub_row, '12');
      assert.equal(inputs[annual ? 'selected_month' : 'month'], month.startsWith('7') ? '2026-07' : '2026-05');
      if (annual) assert.equal(inputs.financial_years, '2026-27');
      for (const input of Object.keys(inputs)) assert.ok(contracts[workflow].includes(input), `${workflow} rejects ${input}`);
    }
  }
}
assert.equal(calls.length, 12);
assert.equal(ctx.hubFY_('2026-03'), '2025-26');
assert.equal(ctx.hubFY_('2026-04'), '2026-27');
console.log('12 depot/month/service dispatch contracts and FY boundaries passed');

for (const depot of ['PRODDUTUR', 'RAJAMPET']) {
  ctx.onHubSubmit({namedValues: {Depot: [depot], 'Required Service / Report': ['Daily HSD KMPL Report'], 'Report Date': ['2026-05-12']}, range: {getSheet: () => ({}), getRow: () => 13}});
  const {workflow, inputs} = calls.at(-1);
  assert.equal(workflow, 'daily-report.yml');
  assert.deepEqual(JSON.parse(JSON.stringify(inputs)), {depot, report_date: '2026-05-12', hub_row: '13'});
  for (const input of Object.keys(inputs)) assert.ok(contracts[workflow].includes(input), `${workflow} rejects ${input}`);
}
console.log('2 daily Hub dispatch contracts passed');
