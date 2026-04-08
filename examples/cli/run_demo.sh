#!/usr/bin/env bash
set -euo pipefail

REFERENCE="samples/reference.wav"
SINGLE_TAKE="samples/take.wav"
BATCH_TAKE_1="samples/take_01.wav"
BATCH_TAKE_2="samples/take_02.wav"
BATCH_TAKE_3="samples/take_03.wav"

echo "--- single analysis ---"
practicelens analyze \
  --reference "$REFERENCE" \
  --take "$SINGLE_TAKE" \
  --out out/single

echo
echo "Generated single artifacts:"
ls -1 out/single || true

echo
echo "--- batch comparison ---"
practicelens compare-batch \
  --reference "$REFERENCE" \
  --take "$BATCH_TAKE_1" \
  --take "$BATCH_TAKE_2" \
  --take "$BATCH_TAKE_3" \
  --out out/batch

echo
echo "Generated batch artifacts:"
ls -1 out/batch || true

echo
echo "Done. Open these first:"
echo "  out/single/report.svg"
echo "  out/single/report.md"
echo "  out/batch/batch_report.svg"
echo "  out/batch/batch_report.md"
