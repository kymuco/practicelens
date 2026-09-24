# Measurement Contract v1

Status: R0.2  
Schema version: 1

## Purpose

This contract makes controlled PracticeLens measurement experiments reproducible before the project changes any scoring semantics.

It deliberately does not answer whether a score is valid. It records enough information to ask that question without losing the conditions under which a value was produced.

## Contract boundary

One `MeasurementExperimentRecord` represents one controlled condition:

```text
experiment identity
+ reference/take identity
+ intervention identity and strength
+ exact analysis configuration
+ generator/revision provenance
+ candidate measurement outputs
```

The record is evidence metadata, not a scientific verdict.

## Intervention roles

Every controlled condition has exactly one primary role:

- `control` — zero-change baseline for an intervention family;
- `nuisance` — variation that should not masquerade as the target construct;
- `target` — deliberate variation intended to challenge a candidate measurement.

A control intervention must have `strength = 0.0`.

The `family` and `unit` fields remain explicit rather than inferred from filenames.

Examples:

```text
family=amplitude_gain
role=nuisance
strength=-6.0
unit=db
```

```text
family=pitch_drift
role=target
strength=0.02
unit=fraction
```

## Exact configuration snapshot

The contract snapshots every current `AnalysisConfig` field used by the deterministic baseline:

- analysis schema version;
- target sample rate;
- frame length;
- hop length;
- segment duration;
- all four score weights.

The audit must not silently compare records produced under different configurations as though they were the same instrument.

## Provenance

The v1 provenance surface contains:

- generator identity;
- generator version;
- optional source manifest;
- optional code revision;
- exact analysis configuration snapshot.

Wall-clock time is intentionally absent from the canonical record. It is not required to reproduce a deterministic controlled condition and would make otherwise identical records differ.

If later experiments require environment provenance, it should be added explicitly in a new additive schema revision rather than hidden inside free-form text.

## Candidate measurement results

A result contains:

- stable measurement name;
- finite numeric value;
- explicit unit;
- explicit source.

Example:

```json
{
  "name": "pitch_fidelity",
  "value": 83.25,
  "unit": "score_0_100",
  "source": "component_score"
}
```

The word `candidate` is intentional. Capturing `pitch_fidelity=83.25` does not establish construct validity.

## Canonical payload

The serializer produces:

```text
kind = measurement_experiment_record
schema_version = 1
```

and deterministic JSON using sorted keys.

The payload is intended to become the input record for R0.3 and R0.4 tooling.

## Invariants

Schema v1 requires:

1. non-empty experiment and condition identities;
2. non-empty reference/take case identities;
3. finite intervention strengths;
4. zero strength for `control`;
5. unique intervention parameter names;
6. at least one candidate measurement;
7. unique measurement names within a record;
8. finite measurement values;
9. exact supported schema version.

These invariants are deliberately structural. R0.2 must not encode expected scientific outcomes such as "pitch drift should reduce pitch fidelity". Those expectations belong to the later audit protocol.

## Non-goals

R0.2 does not:

- generate perturbations;
- run the analysis pipeline;
- change current scores;
- define PASS/FAIL thresholds;
- claim sensitivity or specificity;
- add an event representation;
- add ML;
- export HDE skill signals.

## Next step

R0.3 will use this contract to build parameterized controlled perturbation families with zero-change controls and ordered intervention strengths.

The critical rule remains:

> The controlled harness describes what was changed. It does not modify the measurement instrument to make the expected result appear.
