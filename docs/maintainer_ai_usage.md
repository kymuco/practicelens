# Maintainer AI Usage

PracticeLens may use AI coding tools to support open-source maintenance work, but project changes remain maintainer-reviewed before they are merged.

## Intended use

AI tools may be used for:

- issue triage and summarization;
- pull request review assistance;
- test generation and edge-case exploration;
- documentation drafts and copyediting;
- release checklist preparation;
- contributor workflow improvements;
- analysis of deterministic audio-diagnostic behavior;
- maintaining examples, evaluation assets, and report contracts.

## Boundaries

AI assistance should not replace maintainer judgment.

For PracticeLens, this means:

- no unreviewed AI-generated code should be merged;
- scoring, ranking, alignment, and report semantics must remain explainable;
- changes that affect CLI, API, artifact formats, or report contracts must be reviewed explicitly;
- generated examples and evaluation assets should stay reproducible and documented;
- user audio and private practice recordings should not be committed to the repository;
- local-first behavior and explicit opt-in history remain part of the project direction.

## API credits and open-source support

If PracticeLens receives API credits or open-source program support, the intended use is to improve the public open-source project and its maintainer workflow.

Expected areas include:

- improving tests around CLI, API, and report behavior;
- reviewing pull requests and proposed implementation plans;
- improving documentation and onboarding paths;
- checking edge cases in input suitability and confidence warnings;
- preparing release notes and changelogs;
- improving generated evaluation/showcase workflows;
- maintaining issue quality for small, reviewable contributor tasks.

Future integration contracts may be explored when they directly improve PracticeLens as an independent open-source music-practice analysis toolkit. Broader private or unrelated systems are outside the intended use of PracticeLens-specific open-source support.
