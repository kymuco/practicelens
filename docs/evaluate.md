# How to Evaluate PracticeLens

This guide is for someone opening the repository and wanting to answer one question quickly:

**is this a real, disciplined project or just a pile of code?**

## Fast evaluation path

### 1. Look at the first screen

Start with:

- `README.md`
- CI badge
- quickstart links
- architecture and repository-map links

You should be able to understand the project direction without reading source code first.

### 2. Verify trust signals

Check that the repo has:

- green CI;
- contribution and security docs;
- issue and PR templates;
- changelog;
- development guide.

These do not prove product quality by themselves, but they strongly reduce the odds that the repo is unmanaged.

### 3. Verify there is a real working slice

Look for:

- CLI support for single-take analysis;
- batch comparison support;
- API support for single and batch flows;
- generated report artifacts;
- tests covering real user-facing flows.

The key question is not whether everything is finished.
The key question is whether the project already has a coherent, runnable vertical slice.

### 4. Read architecture before deep code browsing

Use:

- `docs/architecture.md`
- `docs/repository-map.md`

This should tell you:

- what the layers are;
- where orchestration lives;
- where scoring lives;
- where reporting lives;
- how CLI and API fit on top.

### 5. Check examples and payloads

Use:

- `docs/quickstart.md`
- `docs/api.md`
- `examples/cli/README.md`
- `examples/api/*.json`

A repo feels much more trustworthy when the intended usage path is visible and copyable.

### 6. Inspect boundaries, not just file count

A useful repo is not judged only by size.

Look for boundary quality instead:

- deterministic core vs thin outer surfaces;
- explainable scoring vs black-box claims;
- stable artifact shapes;
- explicit API payload contracts;
- tests covering actual entry flows.

## What a good outcome looks like

After a short evaluation, you should be able to say:

- what PracticeLens does;
- what it already supports;
- what it deliberately does not support yet;
- how to run it;
- how to review its architecture;
- where it is likely headed next.

If those answers are obvious, the repo is already doing something right.
