# Optional daily tyre details

Generate the regular daily report first using the unchanged application and
calculations. Only after its output file exists, the automated runner calls the
separate tyre module. Upload and existing Telegram delivery use that combined
file; no separate tyre message is introduced.

Scheduled requests and manual today resolve to yesterday in Asia/Kolkata.
Earlier selected dates remain unchanged. Check the resolved date: odd dates
fetch RC front tyres and mismatched tyres; even dates make no tyre requests.
Repair tyres are excluded.

POST rc_tyres_front1.php with fyymm=D/M/YYYY, then rcpopup.php and
samepopup.php with dt=D/M/YYYY, regn=mapped district, dept blank. Filter the
district response by exact normalized depot identity; validate heading date,
vehicle and tyre-position columns. Never interpret unavailable data as zero.

Display Telugu category counts, vehicle numbers and tyre positions only.
Omit each category with zero rows. When both are zero, preserve the daily text
exactly with no tyre heading or completion marker. A valid positive RC-front
result still displays when mismatched tyres are zero. Source/authentication
failure adds a short unavailable note while preserving the completed daily
content. Replace the local combined file atomically.

Existing cached Drive reports keep the original reuse behavior. This change
does not refresh previously uploaded reports or modify the Drive integration.

Validation: 21 focused tests passed and changed Python modules compiled.
Coverage includes zero/positive category combinations, odd/even dates, source
validation, source failures, depot isolation and daily-before-tyres ordering.
The 13 previously observed failures on unchanged master remain unresolved.
This draft has not been merged or verified through live Hub/Telegram delivery.
