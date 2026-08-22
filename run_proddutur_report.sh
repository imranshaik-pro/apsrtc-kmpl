#!/bin/bash
# run_proddutur_report.sh - Generate APSRTC report and upload to Google Drive

cd /home/imran/apsrtc-kmpl || exit 1
source .venv/bin/activate

REPORT_DATE=$(date -d "yesterday" +%Y-%m-%d)
REPORT_FILE="reports/PRODDUTUR_${REPORT_DATE}.txt"
LOG_FILE="/home/imran/apsrtc-kmpl/logs/report.log"
GDRIVE_FOLDER="1tU9aw7Cdw-Q-7mr9BMhayORKMy61_DOz"

# ---------- Report generation retry ----------
MAX_RETRIES=3
RETRY_DELAY=300  # 5 minutes

for attempt in $(seq 1 $MAX_RETRIES); do
    echo "Attempt $attempt of $MAX_RETRIES at $(date)" >> "$LOG_FILE"
    
    python run_daily_report.py --date "$REPORT_DATE" --depot PRODDUTUR --vehicle-depot "PDTR/PRODDUTUR" --region-code YSRKADAPA >> "$LOG_FILE" 2>&1
    
    if [ -f "$REPORT_FILE" ] && [ -s "$REPORT_FILE" ]; then
        echo "Report generated successfully on attempt $attempt at $(date)" >> "$LOG_FILE"
        break
    fi
    
    echo "Attempt $attempt failed or report missing. Waiting $RETRY_DELAY seconds..." >> "$LOG_FILE"
    sleep $RETRY_DELAY
done

if [ ! -f "$REPORT_FILE" ] || [ ! -s "$REPORT_FILE" ]; then
    echo "All $MAX_RETRIES attempts failed. Report not generated at $(date)" >> "$LOG_FILE"
    deactivate
    exit 1
fi

# ---------- Upload to Google Drive ----------
UPLOAD_RETRIES=3
UPLOAD_DELAY=60  # 1 minute

for attempt in $(seq 1 $UPLOAD_RETRIES); do
    echo "Upload attempt $attempt of $UPLOAD_RETRIES at $(date)" >> "$LOG_FILE"
    
    gdrive files upload --parent "$GDRIVE_FOLDER" "$REPORT_FILE" >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        echo "Upload successful on attempt $attempt at $(date)" >> "$LOG_FILE"
        deactivate
        exit 0
    fi
    
    echo "Upload attempt $attempt failed. Waiting $UPLOAD_DELAY seconds..." >> "$LOG_FILE"
    sleep $UPLOAD_DELAY
done

echo "All $UPLOAD_RETRIES upload attempts failed. Report file exists but not uploaded." >> "$LOG_FILE"
deactivate
exit 1
