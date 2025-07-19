#!/bin/bash
set -e

# Source config functions
source /usr/src/app/config.shlib;

echo "Reading configuration..."
TZ="$(config_get timezone General)";
CRON_SCHEDULE="$(config_get crontab General)";
RUN_ONCE="$(config_get run_once General | tr -cd '[:alnum:]')";
RUN_ON_STARTUP="$(config_get run_on_startup General | tr -cd '[:alnum:]')";

echo "Configuration values:"
echo "  Timezone: '$TZ'"
echo "  Cron schedule: '$CRON_SCHEDULE'"
echo "  Run once: '$RUN_ONCE'"
echo "  Run on startup: '$RUN_ON_STARTUP'"

# Set default timezone if empty
if [ -z "$TZ" ]; then
    TZ="UTC"
    echo "Using default timezone: $TZ"
fi

export MOZ_HEADLESS=1
echo "Setting timezone: $TZ"

# Check if timezone file exists before creating symlink
if [ -f "/usr/share/zoneinfo/$TZ" ]; then
    rm -rf /etc/localtime
    ln -s "/usr/share/zoneinfo/$TZ" /etc/localtime
    echo "Timezone set successfully"
else
    echo "Warning: Timezone file /usr/share/zoneinfo/$TZ not found, using system default"
fi

echo "Run on startup: ${RUN_ON_STARTUP}"
if [ "$RUN_ON_STARTUP" = "true" ]; then
    echo "Executing speedtest..."
    "/usr/src/app/speedtest.py" > /proc/self/fd/1 2>/proc/self/fd/2
    if [ "$RUN_ONCE" = "true" ]; then
        echo "Run once: ${RUN_ONCE}"
        echo "Exiting..."
        exit 0
    fi
fi

echo "Run once: ${RUN_ONCE}"
if [ "$RUN_ONCE" = "false" ]; then
    echo "Setting up cron job..."
    printenv | sed 's/^\(.*\)$/export \1/g' > /root/project_env.sh
    echo "Setting cron schedule: ${CRON_SCHEDULE}"
    # Fix cron schedule format - remove escaped asterisks and ensure proper format
    FIXED_CRON_SCHEDULE=$(echo "${CRON_SCHEDULE}" | sed 's/\\//g')
    echo "Fixed cron schedule: ${FIXED_CRON_SCHEDULE}"
    echo "${FIXED_CRON_SCHEDULE} . /root/project_env.sh && '/usr/src/app/speedtest.py' > /proc/self/fd/1 2>/proc/self/fd/2" | crontab -
    echo "Current crontab:"
    crontab -l
    echo "Starting cron daemon..."
    cron -f
else
    echo "Running speedtest once..."
    "/usr/src/app/speedtest.py" > /proc/self/fd/1 2>/proc/self/fd/2
    echo "Exiting..."
    exit 0
fi