#!/bin/bash
REPORT_DATE=$(date -d "yesterday" +%Y-%m-%d)
REPORT_FILE="/home/imran/apsrtc-kmpl/reports/PRODDUTUR_${REPORT_DATE}.txt"
GDRIVE_FOLDER="1tU9aw7Cdw-Q-7mr9BMhayORKMy61_DOz"
LOG_MEMORY="/home/imran/apsrtc-kmpl/logs/memory_usage.log"

mkdir -p /home/imran/apsrtc-kmpl/logs

# Start container in detached mode
CONTAINER_ID=$(docker run -d \
  -v /home/imran/apsrtc-kmpl/.env:/app/.env \
  -v /home/imran/apsrtc-kmpl/depot_mapping.json:/app/depot_mapping.json \
  -v /home/imran/apsrtc-kmpl/reports:/app/reports \
  apsrtc-report \
  python run_daily_report.py --date "$REPORT_DATE" --depot PRODDUTUR --vehicle-depot "PDTR/PRODDUTUR" --region-code YSRKADAPA)

echo "Container ID: $CONTAINER_ID" >> "$LOG_MEMORY"

# Start memory logging
docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}" $CONTAINER_ID | tee -a "$LOG_MEMORY" &
STATS_PID=$!

# Wait for container to finish
docker wait $CONTAINER_ID > /dev/null

# Stop stats logging
kill $STATS_PID 2>/dev/null
wait $STATS_PID 2>/dev/null

# Extract peak memory
PEAK=$(tail -n 20 "$LOG_MEMORY" | grep -oP '\d+\.\d+MiB' | sort -n | tail -1)
echo "Peak memory usage: $PEAK" >> "$LOG_MEMORY"
echo "Peak memory usage: $PEAK"

# Upload to Google Drive
if [ -f "$REPORT_FILE" ] && [ -s "$REPORT_FILE" ]; then
    /usr/local/bin/gdrive files upload --parent "$GDRIVE_FOLDER" "$REPORT_FILE"
fi
