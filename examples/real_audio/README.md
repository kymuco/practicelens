# Real Audio Smoke Workflow

This folder intentionally contains documentation only.

Do not commit real recordings, generated reports, session manifests, or local history files to this repository. User audio should remain local and private.

For broader recording expectations and interpretation notes, see [`docs/real_audio_usage.md`](../../docs/real_audio_usage.md).

## 1. Create a local working folder

Use a folder outside the repository, or a clearly local/private folder that you do not commit.

Example layout:

```text
~/PracticeLensLocal/real_audio_smoke/
  audio/
    reference.wav
    take_01.wav
    take_02.wav
    take_03.wav
  out/
  history/
```

Recommended first test:

```text
reference.wav  -> clean reference phrase, 5-15 seconds
take_01.wav    -> one complete attempt of the same phrase
take_02.wav    -> another complete attempt
take_03.wav    -> another complete attempt
```

Keep the first smoke test boring and controlled: same phrase, similar tempo target, minimal effects, no long unrelated intro/outro, and no restart inside a take.

## 2. Set path placeholders

Copy and adjust these placeholders for your machine:

```bash
REAL_AUDIO_DIR="$HOME/PracticeLensLocal/real_audio_smoke"
REFERENCE="$REAL_AUDIO_DIR/audio/reference.wav"
TAKE_01="$REAL_AUDIO_DIR/audio/take_01.wav"
TAKE_02="$REAL_AUDIO_DIR/audio/take_02.wav"
TAKE_03="$REAL_AUDIO_DIR/audio/take_03.wav"
SESSION_OUT="$REAL_AUDIO_DIR/out/session_001"
HISTORY_INDEX="$REAL_AUDIO_DIR/history/index.jsonl"
```

Create output/history folders locally:

```bash
mkdir -p "$REAL_AUDIO_DIR/out" "$REAL_AUDIO_DIR/history"
```

## 3. Run a practice session

Use repeated `--take` arguments for multiple takes:

```bash
practicelens practice-session \
  --reference "$REFERENCE" \
  --take "$TAKE_01" \
  --take "$TAKE_02" \
  --take "$TAKE_03" \
  --out "$SESSION_OUT" \
  --history-index "$HISTORY_INDEX"
```

Optional analysis knobs for experimentation:

```bash
practicelens practice-session \
  --reference "$REFERENCE" \
  --take "$TAKE_01" \
  --take "$TAKE_02" \
  --take "$TAKE_03" \
  --out "$SESSION_OUT" \
  --history-index "$HISTORY_INDEX" \
  --sample-rate 16000 \
  --frame-length 2048 \
  --hop-length 512 \
  --segment-duration 8.0
```

## 4. Inspect these outputs first

Start with the top-level session artifacts:

```text
$SESSION_OUT/practice_plan.md
$SESSION_OUT/batch_report.md
$SESSION_OUT/session_manifest.json
```

Suggested reading order:

1. `practice_plan.md` — what to practice before the next recording;
2. `batch_report.md` — which take ranked best and why;
3. `session_manifest.json` — machine-readable session summary and artifact map.

Then inspect per-take folders:

```text
$SESSION_OUT/takes/
  01-take_01/
    report.md
    practice_plan.md
    debug_payload.json
  02-take_02/
    report.md
    practice_plan.md
    debug_payload.json
  03-take_03/
    report.md
    practice_plan.md
    debug_payload.json
```

For a fast human review, open each take's `report.md` and `practice_plan.md` first. Use `debug_payload.json` only when you need lower-level diagnostic details.

## 5. List recorded sessions

After running at least one `practice-session` with `--history-index`, list indexed sessions:

```bash
practicelens sessions list \
  --history-index "$HISTORY_INDEX" \
  --limit 5
```

## 6. Show one session

Show by indexed session id:

```bash
practicelens sessions show 1 \
  --history-index "$HISTORY_INDEX"
```

You can also show by session directory or manifest path:

```bash
practicelens sessions show "$SESSION_OUT" \
  --history-index "$HISTORY_INDEX"

practicelens sessions show "$SESSION_OUT/session_manifest.json" \
  --history-index "$HISTORY_INDEX"
```

## 7. Compare two sessions

Record a second session after practicing:

```bash
SESSION_OUT_2="$REAL_AUDIO_DIR/out/session_002"

practicelens practice-session \
  --reference "$REFERENCE" \
  --take "$TAKE_01" \
  --take "$TAKE_02" \
  --take "$TAKE_03" \
  --out "$SESSION_OUT_2" \
  --history-index "$HISTORY_INDEX"
```

Then compare session 1 and session 2 by history id:

```bash
practicelens sessions compare 1 2 \
  --history-index "$HISTORY_INDEX"
```

Or compare explicit manifest paths:

```bash
practicelens sessions compare \
  "$SESSION_OUT/session_manifest.json" \
  "$SESSION_OUT_2/session_manifest.json" \
  --history-index "$HISTORY_INDEX"
```

## 8. Privacy and repository hygiene

Keep these local/private:

```text
*.wav
*.mp3
*.flac
*.m4a
out/
history/index.jsonl
session_manifest.json
report.json
report.md
practice_plan.md
batch_report.json
batch_report.md
debug_payload.json
```

Before committing, check that only documentation changed:

```bash
git status --short
```

Expected for this example docs folder:

```text
?? examples/real_audio/README.md
```

Do not commit the `audio/`, `out/`, or `history/` folders from your local smoke test.

## 9. Quick interpretation checklist

If the Markdown reports include confidence or suitability warnings, fix the recording before trusting detailed feedback too much.

Good next recording target:

```text
same phrase as reference
complete take
clear first note/attack
short leading silence only
minimal room/pickup/handling noise
no false start or restart
no unrelated material before or after the phrase
```

If the first smoke test looks strange, rerecord a shorter and cleaner 5-15 second phrase before changing PracticeLens parameters.
