#!/bin/bash
cd /home/imran/apsrtc-kmpl
source .venv/bin/activate
REPORT_DATE=$(date -d "yesterday" +%Y-%m-%d)
python run_daily_report.py --date $REPORT_DATE --depot PRODDUTUR --vehicle-depot "PDTR/PRODDUTUR" --region-code YSRKADAPA >> /home/imran/apsrtc-kmpl/logs/report.log 2>&1
deactivate
