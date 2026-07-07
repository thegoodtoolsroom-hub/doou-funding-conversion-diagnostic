You are building the DOO U Grant Funding Conversion Diagnostic as a deterministic commercial report automation product.

I am not a developer. Do not assume I can fix code. Build slowly, test everything, and tell me exactly what you changed.

Use these folders as the only source of truth:
- product_lock/
- survey/
- templates/
- test_data/

Do not use old framework files. Do not invent a new framework. Do not redesign the report.

Canonical product structure:
- 12 client-facing report variables
- 24 assessment areas/drivers
- 121 metric signals
- report-version weights totaling 100%
- LimeSurvey export decoding
- protected evidence and unsafe route flags
- Word DOCX report template as the master paid report design

Hard rules:
1. Build the engine first, not the UI.
2. Never generate a client-facing report from zero scored survey signals.
3. Never silently default all variables to 50%.
4. The 5 dummy test responses must create 5 different report patterns.
5. The Full Report must use the Word template, not generic HTML.
6. The PDF must use Verdana or fail with a clear font QA error.

First task only:
Inspect the repository files and confirm that you can see:
- product lock workbook
- 12 variable lock CSV
- 24 assessment area lock CSV
- 121 metric registry template CSV
- locked LimeSurvey LSS
- master Word report template
- 5 dummy batch response files
- expected QA patterns JSON

Then create the repository folder structure and a short implementation plan. Do not build the full app yet.
