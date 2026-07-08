# DOO U Grant Funding Conversion Diagnostic

Deterministic report automation product for the DOO U Grant Funding Conversion Diagnostic.

## Current Build Stage

Ticket 06R commercial output QA layer in progress.

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
