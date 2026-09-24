/**
 * APSRTC Telegram webhook for Google Apps Script.
 *
 * Deploy this file as a Web App and set Telegram's webhook to the deployment
 * URL. It receives Telegram updates, shows the depot-first APSRTC menu, and
 * dispatches the existing GitHub Actions workflows.
 */

const TELEGRAM_API = 'https://api.telegram.org/bot';
const IST_TZ = 'Asia/Kolkata';

const BOT_COMMANDS = [
  { command: 'start', description: 'Select depot and open the APSRTC menu' },
  { command: 'menu', description: 'Select depot, then report or vehicle event' },
  { command: 'daily', description: 'Select depot and completed daily date' },
  { command: 'monthly', description: 'Select depot and reporting month' },
  { command: 'annual', description: 'Select depot and Annual KPI reporting month' },
  { command: 'event', description: 'Enter a vehicle event and confirm before saving' },
  { command: 'status', description: 'Check command processor response' },
  { command: 'help', description: 'Show usage and response-time information' },
];

function doGet() {
  return ContentService.createTextOutput('APSRTC Telegram webhook is ready.');
}

function doPost(e) {
  try {
    const update = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    handleUpdate_(update);
  } catch (err) {
    console.error('WEBHOOK_UPDATE_FAILED: ' + safeError_(err));
  }
  return ContentService.createTextOutput('ok');
}

function setupTelegramWebhook() {
  const props = getProps_();
  configureCommands_();
  telegram_('setWebhook', {
    url: props.WEBHOOK_URL,
    allowed_updates: JSON.stringify(['message', 'callback_query']),
    drop_pending_updates: 'true',
  });
  const info = telegram_('getWebhookInfo', {});
  console.log(JSON.stringify(info));
  return info;
}

function removeTelegramWebhook() {
  const result = telegram_('deleteWebhook', { drop_pending_updates: 'false' });
  console.log(JSON.stringify(result));
  return result;
}

function configureCommands_() {
  const props = getProps_();
  const scope = JSON.stringify({ type: 'chat', chat_id: props.TELEGRAM_CHAT_ID });
  telegram_('setMyCommands', {
    scope,
    language_code: '',
    commands: JSON.stringify(BOT_COMMANDS),
  });
  telegram_('setMyCommands', {
    scope,
    language_code: 'en',
    commands: JSON.stringify(BOT_COMMANDS),
  });
  if (/^\d+$/.test(String(props.TELEGRAM_CHAT_ID))) {
    telegram_('setChatMenuButton', {
      chat_id: props.TELEGRAM_CHAT_ID,
      menu_button: JSON.stringify({ type: 'commands' }),
    });
  }
  return telegram_('getMyCommands', { scope, language_code: 'en' });
}

function handleUpdate_(update) {
  if (update.callback_query) {
    const cq = update.callback_query;
    const chatId = String(((cq.message || {}).chat || {}).id || '');
    if (!isAuthorized_(chatId)) {
      answerCallback_(cq.id, 'Unauthorized');
      return;
    }
    answerCallback_(cq.id, '');
    handleCallback_(chatId, String(cq.data || ''));
    return;
  }

  const msg = update.message || {};
  const chatId = String((msg.chat || {}).id || '');
  const text = String(msg.text || '').trim();
  if (!chatId) return;
  if (!isAuthorized_(chatId)) {
    send_(chatId, 'Unauthorized chat.');
    return;
  }
  handleMessage_(chatId, text);
}

function handleMessage_(chatId, text) {
  const state = getState_();
  if (state && !text.startsWith('/')) {
    handleStateMessage_(chatId, text, state);
    return;
  }

  const cmd = String((text.split(/\s+/)[0] || '').split('@')[0]).toLowerCase();
  if (cmd === '/start' || cmd === '/help' || cmd === '/menu') {
    clearState_();
    send_(chatId, helpText_(), mainMenu_());
    return;
  }
  if (cmd === '/status') {
    send_(chatId, '✅ APSRTC automation bot is online.\nAuthorized chat verified.', mainMenu_());
    return;
  }
  if (cmd === '/daily') {
    clearState_();
    send_(chatId, 'Select depot for Daily Report:', depotKeyboard_('daily'));
    return;
  }
  if (cmd === '/monthly') {
    clearState_();
    send_(chatId, 'Select depot for Monthly Report:', depotKeyboard_('monthly'));
    return;
  }
  if (cmd === '/annual') {
    clearState_();
    send_(chatId, 'Select depot for Annual KPI:', depotKeyboard_('annual'));
    return;
  }
  if (cmd === '/event') {
    clearState_();
    send_(chatId, 'Select depot for Vehicle Event:', depotKeyboard_('event'));
    return;
  }
  if (cmd === '/vehicle') {
    send_(chatId, 'Vehicle 360 lookup is the next phase. No report has been triggered.', mainMenu_());
    return;
  }
  send_(chatId, 'Use /menu to open the APSRTC menu.', mainMenu_());
}

function handleCallback_(chatId, data) {
  const parts = data.split('|');
  const depots = depots_();

  if (data === 'menu|depots') {
    clearState_();
    send_(chatId, 'Select depot:', mainMenu_());
    return;
  }
  if (parts.length === 2 && parts[0] === 'depot' && depots.indexOf(parts[1]) !== -1) {
    clearState_();
    send_(chatId, 'Depot: ' + parts[1] + '\nChoose an action:', depotActions_(parts[1]));
    return;
  }
  if (parts.length === 2 && parts[0] === 'vehicle' && depots.indexOf(parts[1]) !== -1) {
    send_(chatId, 'Standalone Vehicle 360 lookup is not yet available. No request was submitted.', depotActions_(parts[1]));
    return;
  }
  if (parts.length === 2 && parts[0] === 'daily' && depots.indexOf(parts[1]) !== -1) {
    send_(chatId, 'Daily Report — ' + parts[1] + '\nChoose completed report date (IST):', dailyDateKeyboard_(parts[1]));
    return;
  }
  if (parts.length === 3 && parts[0] === 'dailyrun' && depots.indexOf(parts[1]) !== -1) {
    if (!isCompletedDate_(parts[2])) {
      send_(chatId, 'Select a completed date before today.', mainMenu_());
      return;
    }
    dispatch_('daily-report.yml', { depot: parts[1], report_date: parts[2] });
    send_(chatId, 'Daily report requested\nDepot: ' + parts[1] + '\nReport date: ' + displayIsoDate_(parts[2]) + '\nThe report will be delivered when generation finishes.', depotActions_(parts[1]));
    return;
  }
  if (parts.length === 2 && parts[0] === 'monthly' && depots.indexOf(parts[1]) !== -1) {
    send_(chatId, 'Monthly Report — ' + parts[1] + '\nSelect month:', monthKeyboard_(parts[1], 'monthlyrun'));
    return;
  }
  if (parts.length === 3 && parts[0] === 'monthlyrun' && depots.indexOf(parts[1]) !== -1) {
    if (!isAllowedMonth_(parts[2])) {
      send_(chatId, 'Invalid or future month.', mainMenu_());
      return;
    }
    dispatch_('monthly-report.yml', { depot: parts[1], month: parts[2] });
    send_(chatId, '⏳ Monthly report requested for ' + parts[1] + ' — ' + parts[2] + '.', mainMenu_());
    return;
  }
  if (parts.length === 2 && parts[0] === 'annual' && depots.indexOf(parts[1]) !== -1) {
    send_(chatId, 'Annual KPI — ' + parts[1] + '\nSelect reporting month:', monthKeyboard_(parts[1], 'annualrun'));
    return;
  }
  if (parts.length === 3 && parts[0] === 'annualrun' && depots.indexOf(parts[1]) !== -1) {
    if (!isAllowedMonth_(parts[2])) {
      send_(chatId, 'Invalid or future month.', mainMenu_());
      return;
    }
    dispatch_('annual-kpi.yml', {
      depot: parts[1],
      selected_month: parts[2],
      financial_years: financialYear_(parts[2]),
    });
    send_(chatId, 'Annual KPI requested for ' + parts[1] + ' — ' + parts[2] + '. The report link will be sent when complete.', mainMenu_());
    return;
  }
  if (parts.length === 2 && parts[0] === 'event' && depots.indexOf(parts[1]) !== -1) {
    setState_({ step: 'vehicle', depot: parts[1] });
    send_(chatId, 'Depot: ' + parts[1] + '\nReply with the vehicle number:');
    return;
  }
  if (parts.length === 4 && parts[0] === 'etype' && depots.indexOf(parts[1]) !== -1) {
    const eventDate = todayIso_();
    send_(chatId, 'Depot: ' + parts[1] + '\nVehicle: ' + parts[2] + '\n' + parts[3] + ' — select Event Date (IST):', eventDateKeyboard_(parts[1], parts[2], parts[3]));
    return;
  }
  if (parts.length === 5 && parts[0] === 'edate' && depots.indexOf(parts[1]) !== -1) {
    if (!isValidEventDate_(parts[4])) {
      send_(chatId, 'Invalid event date.', mainMenu_());
      return;
    }
    setState_({ step: 'details', depot: parts[1], vehicle: normalizeVehicle_(parts[2]), event_type: parts[3], event_date: parts[4] });
    send_(chatId, eventDetailPrompt_(parts[1], normalizeVehicle_(parts[2]), parts[3], parts[4]));
    return;
  }

  send_(chatId, 'That menu option is no longer valid. Open /menu again.', mainMenu_());
}

function handleStateMessage_(chatId, text, state) {
  if (state.step === 'vehicle') {
    const vehicle = normalizeVehicle_(text);
    if (!vehicle) {
      send_(chatId, 'Invalid vehicle number. Start /event again.', mainMenu_());
      clearState_();
      return;
    }
    clearState_();
    send_(chatId, 'Vehicle: ' + vehicle + '\nSelect Event Type:', eventTypeKeyboard_(state.depot, vehicle));
    return;
  }
  if (state.step === 'details') {
    try {
      const payload = parseEventDetails_(state, text);
      setState_({ step: 'confirm', payload });
      send_(chatId, confirmationText_(payload));
    } catch (err) {
      clearState_();
      send_(chatId, '❌ ' + safeError_(err) + '\nStart /event again.', mainMenu_());
    }
    return;
  }
  if (state.step === 'confirm') {
    const upper = text.toUpperCase();
    if (upper === 'CANCEL') {
      clearState_();
      send_(chatId, 'Vehicle Event cancelled. Nothing was saved.', mainMenu_());
      return;
    }
    if (upper !== 'CONFIRM') {
      send_(chatId, 'Reply CONFIRM to save or CANCEL.');
      return;
    }
    const payload = state.payload;
    const result = postEvent_(payload);
    clearState_();
    send_(chatId, '✅ VEHICLE EVENT RECORDED\nEvent ID: ' + (result.event_id || '') + '\nDepot: ' + payload.depot + '\nVehicle: ' + payload.vehicle_no + '\nType: ' + payload.event_type, mainMenu_());
    return;
  }
  clearState_();
  send_(chatId, 'Use /menu to open the APSRTC menu.', mainMenu_());
}

function helpText_() {
  return '🚌 APSRTC AUTOMATION BOT\n\nSelect your depot, then choose Daily, Monthly, Annual KPI, Vehicle Event, or Vehicle 360.';
}

function mainMenu_() {
  return depotKeyboard_('depot');
}

function depotKeyboard_(action) {
  const depots = depots_();
  if (!depots.length) return [[{ text: 'Depot master not configured', callback_data: 'menu|status' }]];
  const rows = [];
  for (let i = 0; i < depots.length; i += 2) {
    rows.push(depots.slice(i, i + 2).map(d => ({ text: d, callback_data: action + '|' + d })));
  }
  return rows;
}

function depotActions_(depot) {
  return [
    [{ text: 'Daily Report', callback_data: 'daily|' + depot }, { text: 'Monthly Report', callback_data: 'monthly|' + depot }],
    [{ text: 'Annual KPI', callback_data: 'annual|' + depot }, { text: 'Vehicle Event', callback_data: 'event|' + depot }],
    [{ text: 'Vehicle 360 — not yet available', callback_data: 'vehicle|' + depot }],
    [{ text: 'Change depot', callback_data: 'menu|depots' }],
  ];
}

function dailyDateKeyboard_(depot) {
  const rows = [];
  for (let i = 1; i <= 7; i++) {
    const value = addDaysIso_(todayIso_(), -i);
    rows.push([{ text: formatIsoDate_(value), callback_data: 'dailyrun|' + depot + '|' + value }]);
  }
  rows.push([{ text: 'Back to depot options', callback_data: 'depot|' + depot }]);
  return rows;
}

function monthKeyboard_(depot, action) {
  const now = todayParts_();
  let year = now.year;
  let month = now.month;
  const rows = [];
  for (let i = 0; i < 6; i++) {
    const value = year + '-' + pad2_(month);
    rows.push([{ text: monthName_(year, month), callback_data: action + '|' + depot + '|' + value }]);
    month -= 1;
    if (month === 0) {
      month = 12;
      year -= 1;
    }
  }
  return rows;
}

function eventTypeKeyboard_(depot, vehicle) {
  return [
    [{ text: '🔧 Unit Change', callback_data: 'etype|' + depot + '|' + vehicle + '|UNIT CHANGE' }],
    [{ text: '❌ Breakdown', callback_data: 'etype|' + depot + '|' + vehicle + '|BREAKDOWN' }],
    [{ text: '🛞 Tyre Change', callback_data: 'etype|' + depot + '|' + vehicle + '|TYRE CHANGE' }],
    [{ text: 'III Schedule III', callback_data: 'etype|' + depot + '|' + vehicle + '|SCHEDULE III' }],
    [{ text: 'IV Schedule IV', callback_data: 'etype|' + depot + '|' + vehicle + '|SCHEDULE IV' }],
  ];
}

function eventDateKeyboard_(depot, vehicle, eventType) {
  const rows = [];
  for (let i = 0; i < 7; i++) {
    const value = addDaysIso_(todayIso_(), -i);
    rows.push([{ text: formatIsoDate_(value), callback_data: 'edate|' + depot + '|' + vehicle + '|' + eventType + '|' + value }]);
  }
  return rows;
}

function eventDetailPrompt_(depot, vehicle, eventType, eventDate) {
  let guide = 'Reply with Remarks, or - if none.';
  if (eventType === 'BREAKDOWN') guide = 'Reply: Location | KM Cancelled | Breakdown Details | Remarks';
  if (eventType === 'TYRE CHANGE') guide = 'Reply: Position: Tyre No | Position: Tyre No | Remarks\nUse only FOS/FNS/ROSO/ROSI/RNSO/RNSI/SPARE positions.';
  if (eventType === 'UNIT CHANGE') guide = 'Reply: Components | Spring Positions | Remarks\nUse spring positions only FOS/FNS/ROS/RNS; use - when not applicable.';
  return 'EVENT DETAILS [' + depot + '|' + vehicle + '|' + eventType + '|' + eventDate + ']\n' + guide;
}

function parseEventDetails_(state, text) {
  const payload = {
    depot: state.depot,
    vehicle_no: state.vehicle,
    event_type: state.event_type,
    event_date: state.event_date,
    components: '',
    spring_positions: '',
    tyre_history: '',
    breakdown_location: '',
    kms_cancelled: '',
    breakdown_details: '',
    remarks: '',
  };
  if (state.event_type === 'BREAKDOWN') {
    const vals = text.split('|').map(s => s.trim());
    if (vals.length < 3) throw new Error('Use: Location | KM Cancelled | Breakdown Details | Remarks');
    payload.breakdown_location = vals[0];
    payload.kms_cancelled = vals[1];
    payload.breakdown_details = vals[2];
    payload.remarks = vals.slice(3).join(' | ');
  } else if (state.event_type === 'UNIT CHANGE') {
    const vals = text.split('|').map(s => s.trim());
    payload.components = vals[0] === '-' ? '' : (vals[0] || '');
    payload.spring_positions = !vals[1] || vals[1] === '-' ? '' : vals[1];
    payload.remarks = !vals[2] || vals[2] === '-' ? '' : vals.slice(2).join(' | ');
    if (!payload.components && !payload.spring_positions) throw new Error('Enter component or spring details.');
  } else if (state.event_type === 'TYRE CHANGE') {
    const allowed = ['FOS', 'FNS', 'ROSO', 'ROSI', 'RNSO', 'RNSI', 'SPARE'];
    const tyre = [];
    const remarks = [];
    text.split('|').map(s => s.trim()).forEach(v => {
      const key = v.split(':', 1)[0].trim().toUpperCase();
      if (v.indexOf(':') !== -1 && allowed.indexOf(key) !== -1) tyre.push(v);
      else if (v && v !== '-') remarks.push(v);
    });
    if (!tyre.length) throw new Error('Enter at least one tyre as Position: Tyre No.');
    payload.tyre_history = tyre.join(' | ');
    payload.remarks = remarks.join(' | ');
  } else {
    payload.remarks = text.trim() === '-' ? '' : text.trim();
  }
  return payload;
}

function confirmationText_(payload) {
  const lines = [
    '🛠 REVIEW VEHICLE EVENT',
    'Depot: ' + payload.depot,
    'Vehicle: ' + payload.vehicle_no,
    'Date: ' + payload.event_date,
    'Type: ' + payload.event_type,
  ];
  [
    ['components', 'Components'],
    ['spring_positions', 'Spring'],
    ['tyre_history', 'Tyres'],
    ['breakdown_location', 'Location'],
    ['kms_cancelled', 'KM Cancelled'],
    ['breakdown_details', 'Details'],
    ['remarks', 'Remarks'],
  ].forEach(([key, label]) => {
    if (payload[key]) lines.push(label + ': ' + payload[key]);
  });
  lines.push('', 'Reply CONFIRM to save permanently, or CANCEL.');
  return lines.join('\n');
}

function dispatch_(workflow, inputs) {
  const props = getProps_();
  const url = 'https://api.github.com/repos/' + props.GITHUB_REPOSITORY + '/actions/workflows/' + workflow + '/dispatches';
  const response = UrlFetchApp.fetch(url, {
    method: 'post',
    contentType: 'application/json',
    headers: {
      Authorization: 'Bearer ' + props.GH_DISPATCH_TOKEN,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
    },
    payload: JSON.stringify({ ref: props.GITHUB_REF_NAME || 'master', inputs }),
    muteHttpExceptions: true,
  });
  if (response.getResponseCode() !== 204) {
    throw new Error('GitHub dispatch failed for ' + workflow + ': HTTP ' + response.getResponseCode());
  }
}

function postEvent_(payload) {
  const props = getProps_();
  const sep = props.VEHICLE_EVENTS_API_URL.indexOf('?') === -1 ? '?' : '&';
  const response = UrlFetchApp.fetch(props.VEHICLE_EVENTS_API_URL + sep + 'key=' + encodeURIComponent(props.VEHICLE_EVENTS_API_KEY), {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload),
    muteHttpExceptions: true,
  });
  const body = JSON.parse(response.getContentText() || '{}');
  if (response.getResponseCode() >= 300 || !body.ok) throw new Error(body.error || 'Vehicle Event API rejected event');
  return body;
}

function send_(chatId, text, keyboard) {
  const params = { chat_id: chatId, text, disable_web_page_preview: 'true' };
  if (keyboard) params.reply_markup = JSON.stringify({ inline_keyboard: keyboard });
  return telegram_('sendMessage', params);
}

function answerCallback_(callbackId, text) {
  if (!callbackId) return;
  try {
    telegram_('answerCallbackQuery', { callback_query_id: callbackId, text: text || '' });
  } catch (err) {
    console.warn('CALLBACK_ACK_FAILED: ' + safeError_(err));
  }
}

function telegram_(method, params) {
  const props = getProps_();
  const response = UrlFetchApp.fetch(TELEGRAM_API + props.TELEGRAM_BOT_TOKEN + '/' + method, {
    method: 'post',
    payload: params || {},
    muteHttpExceptions: true,
  });
  const body = JSON.parse(response.getContentText() || '{}');
  if (response.getResponseCode() >= 300 || body.ok === false) {
    throw new Error('Telegram ' + method + ' failed: HTTP ' + response.getResponseCode());
  }
  return body;
}

function getProps_() {
  const values = PropertiesService.getScriptProperties().getProperties();
  ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID', 'GH_DISPATCH_TOKEN', 'DEPOT_MASTER', 'GITHUB_REPOSITORY', 'GITHUB_REF_NAME'].forEach(key => {
    if (!values[key]) throw new Error('Missing script property: ' + key);
  });
  return values;
}

function depots_() {
  return String(getProps_().DEPOT_MASTER || '').split('|').map(s => s.trim().toUpperCase()).filter(Boolean);
}

function isAuthorized_(chatId) {
  return String(chatId) === String(getProps_().TELEGRAM_CHAT_ID);
}

function getState_() {
  const raw = PropertiesService.getScriptProperties().getProperty('CHAT_STATE');
  return raw ? JSON.parse(raw) : null;
}

function setState_(state) {
  PropertiesService.getScriptProperties().setProperty('CHAT_STATE', JSON.stringify(state));
}

function clearState_() {
  PropertiesService.getScriptProperties().deleteProperty('CHAT_STATE');
}

function normalizeVehicle_(value) {
  let vehicle = String(value || '').toUpperCase().replace(/[^A-Z0-9]/g, '');
  if (vehicle.indexOf('AP') === 0) vehicle = vehicle.slice(2);
  return /^(?:[A-Z]{2})?[0-9]{2}[A-Z]{1,3}[0-9]{4}$/.test(vehicle) ? vehicle : '';
}

function todayIso_() {
  return Utilities.formatDate(new Date(), IST_TZ, 'yyyy-MM-dd');
}

function todayParts_() {
  return {
    year: Number(Utilities.formatDate(new Date(), IST_TZ, 'yyyy')),
    month: Number(Utilities.formatDate(new Date(), IST_TZ, 'M')),
  };
}

function addDaysIso_(iso, days) {
  const parts = iso.split('-').map(Number);
  const d = new Date(Date.UTC(parts[0], parts[1] - 1, parts[2]));
  d.setUTCDate(d.getUTCDate() + days);
  return Utilities.formatDate(d, 'UTC', 'yyyy-MM-dd');
}

function formatIsoDate_(iso) {
  const parts = iso.split('-').map(Number);
  return Utilities.formatDate(new Date(Date.UTC(parts[0], parts[1] - 1, parts[2])), 'UTC', 'dd MMM yyyy');
}

function displayIsoDate_(iso) {
  const parts = iso.split('-').map(Number);
  return Utilities.formatDate(new Date(Date.UTC(parts[0], parts[1] - 1, parts[2])), 'UTC', 'dd MMMM yyyy');
}

function monthName_(year, month) {
  return Utilities.formatDate(new Date(Date.UTC(year, month - 1, 1)), 'UTC', 'MMMM yyyy');
}

function pad2_(n) {
  return String(n).padStart(2, '0');
}

function isCompletedDate_(iso) {
  return /^\d{4}-\d{2}-\d{2}$/.test(iso) && iso < todayIso_();
}

function isValidEventDate_(iso) {
  return /^\d{4}-\d{2}-\d{2}$/.test(iso) && iso <= todayIso_() && iso >= addDaysIso_(todayIso_(), -6);
}

function isAllowedMonth_(month) {
  return /^\d{4}-\d{2}$/.test(month) && month <= Utilities.formatDate(new Date(), IST_TZ, 'yyyy-MM');
}

function financialYear_(month) {
  const parts = month.split('-').map(Number);
  const start = parts[1] >= 4 ? parts[0] : parts[0] - 1;
  return start + '-' + String(start + 1).slice(-2);
}

function safeError_(err) {
  return String(err && err.message ? err.message : err).replace(/bot[0-9]+:[A-Za-z0-9_-]+/g, 'bot<redacted>');
}
