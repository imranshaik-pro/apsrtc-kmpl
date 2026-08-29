#!/bin/bash
echo "=== Cron job started at $(date) ===" > /home/imran/apsrtc-kmpl/logs/cron_debug.log
echo "PATH: $PATH" >> /home/imran/apsrtc-kmpl/logs/cron_debug.log
echo "PWD: $(pwd)" >> /home/imran/apsrtc-kmpl/logs/cron_debug.log
echo "HOME: $HOME" >> /home/imran/apsrtc-kmpl/logs/cron_debug.log
cd /home/imran/apsrtc-kmpl
./run_proddutur_report.sh >> /home/imran/apsrtc-kmpl/logs/cron_debug.log 2>&1
echo "=== Cron job finished at $(date) ===" >> /home/imran/apsrtc-kmpl/logs/cron_debug.log
