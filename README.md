# DOO U Grant Funding Conversion Diagnostic

Deterministic report automation product for the DOO U Grant Funding Conversion Diagnostic.

## Current Build Stage

Tickets 01–06R are complete.

The engine can now load product lock files, decode LimeSurvey responses, score responses, build report_data, generate batch DOCX/PDF files, and create sample outputs.

Commercial QA correctly blocks the reports because DOCX section injection and Verdana/font verification are not complete yet.

The next required ticket is Ticket 06S: Real Word Template Section Injection.

Ticket 07 web app must not start yet.

The locked source-of-truth folders are:

- `product_lock/`
- `survey/`
- `templates/`
- `test_data/`

Do not build client-facing reports until the engine, decoder, scoring, QA gates, DOCX rendering, and PDF font checks pass.

## Commands

- `make test` runs the smoke test suite.
- `make run` confirms that no UI/app runtime has been built yet.
- `make generate-sample` generates sample batch outputs and writes the commercial QA report.
- `make clean` removes generated working outputs.
