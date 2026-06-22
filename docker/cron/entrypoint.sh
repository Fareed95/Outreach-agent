#!/bin/bash
set -e

echo "Starting Syntrase container..."
echo "Timezone: $(date)"
echo "Environment: $APP_ENV"

# Start cron daemon
service cron start

echo "Cron started. Tailing logs..."

# Keep container alive + stream logs
tail -f /app/logs/agent.log /app/logs/cron.log