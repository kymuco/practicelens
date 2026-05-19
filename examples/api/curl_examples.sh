#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"

curl "$BASE_URL/health"
echo

echo "--- analyze ---"
curl -X POST "$BASE_URL/analyze" \
  -H "Content-Type: application/json" \
  --data @examples/api/analyze_payload.json

echo
echo "--- compare-batch ---"
curl -X POST "$BASE_URL/compare-batch" \
  -H "Content-Type: application/json" \
  --data @examples/api/compare_batch_payload.json

echo
echo "--- practice-session ---"
curl -X POST "$BASE_URL/practice-session" \
  -H "Content-Type: application/json" \
  --data @examples/api/practice_session_payload.json

echo
