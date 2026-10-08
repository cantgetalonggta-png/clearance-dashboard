#!/bin/sh
set -eu
# Idempotent preview bootstrap — bind 0.0.0.0:8080 via npm run dev
if curl -sf -o /dev/null --max-time 1 http://127.0.0.1:8080/; then
  exit 0
fi
cd /workspace
npm run dev >/workspace/artifacts/dev-server.log 2>&1 &
# Wait briefly for readiness
i=0
while [ "$i" -lt 40 ]; do
  if curl -sf -o /dev/null --max-time 1 http://127.0.0.1:8080/; then
    exit 0
  fi
  i=$((i + 1))
  sleep 0.5
done
exit 0
