# Security Policy

## Supported status

PracticeLens is still pre-alpha.

That means:

- the repository is active;
- CI is expected to stay green;
- contracts may still evolve;
- security hardening is not complete.

## Reporting a vulnerability

Please do **not** open a public GitHub issue for a security problem that could expose users, data, or infrastructure.

Instead, report it privately to the repository owner through GitHub security reporting features if enabled, or through a direct private contact path you already have.

When reporting a vulnerability, include:

- what is affected;
- how it can be reproduced;
- impact level;
- whether it affects CLI, API, artifacts, or developer workflow;
- any proof-of-concept details that are necessary to validate the issue.

## Scope expectations

The most relevant current areas include:

- filesystem handling for local artifact generation;
- API payload validation;
- unsafe path handling;
- report artifact writing;
- future uploaded-audio flows.

## Disclosure expectations

Please allow time for validation and a fix before public disclosure.
