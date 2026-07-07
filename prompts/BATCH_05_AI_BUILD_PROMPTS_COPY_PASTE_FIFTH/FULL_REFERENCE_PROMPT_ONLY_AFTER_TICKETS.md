# CODEX BUILD PROMPT — DOO U Grant Funding Conversion Diagnostic Commercial App

You are Codex acting as a senior full-stack product engineer, report automation engineer, LimeSurvey decoder specialist, QA lead, and deployment engineer.

## Project name
DOO U Grant Funding Conversion Diagnostic — Commercial App v1

## Non-negotiable product goal
Build a reliable, paid-service-ready diagnostic automation app that receives LimeSurvey exports or single/batch response CSV/XLSX files, calculates scores from the locked DOO U report framework, generates client-ready DOCX and PDF reports, and blocks report generation when scoring, mapping, fonts, or report QA fails.

This is not a generic dashboard. This is a report automation product with a web app wrapped around it.

## Source of truth
Use the files in the Product Lock Package as the only build authority:

1. `DOO_U_Report_Framework_Product_Lock_Workbook_v1.xlsx`
   - The master product lock workbook.
   - Defines the canonical 12 report variables, 24 assessment areas/drivers, 121 metric registry, stage formulas, score bands, free/full tier rules, QA gates and change-control rules.

2. `DOO_U_LimeSurvey_REPORT_FRAMEWORK_LOCKED_v1.lss`
   - The locked LimeSurvey survey structure.
   - Decode exports by stable question codes and subquestion codes, not by fuzzy full question text.

3. `CSO Grant_Funding_Conversion_Diagnostic_Report_Template.fin(4).docx`
   - The master paid-report visual/content template.
   - Preserve its content, structure, page rhythm, section dividers, colours, headers, footers, images, Verdana body text and premium consulting-report feel.
   - Do not recreate the paid report as a generic HTML dashboard.

4. `DOO_U_5_Dummy_Pilot_Client_Test_Responses_BATCH_LimeSurvey_Code_Style.csv` and individual test files.
   - Use these as QA fixtures.
   - The app must correctly decode all five profiles and produce different result patterns, not default 50% outputs.

## Locked client-facing framework
Use the report-version framework only. Do not use old G-variable labels or the alternate short-name framework.

### 12 report variables
R01 — Context, legal route & compliance — 15% — 17 metrics — B1 Context, Eligibility & Compliance
R02 — Funder intelligence & timing — 6% — 9 metrics — B2 Funding Intelligence & System Discipline
R03 — Fundraising systems & go/no-go — 4% — 9 metrics — B2 Funding Intelligence & System Discipline
R04 — Funder fit & work design — 7% — 11 metrics — B3 Fit, Competitiveness & Access
R05 — Competitive positioning, appeal & ROI — 5% — 8 metrics — B3 Fit, Competitiveness & Access
R06 — Network position & access routes — 5% — 9 metrics — B3 Fit, Competitiveness & Access
R07 — Relationship, leadership & visibility — 8% — 8 metrics — B3 Fit, Competitiveness & Access
R08 — Application quality & storytelling — 4% — 6 metrics — B4 Proposal, Proof, Trust & Ethics
R09 — Coherence, evidence & social proof — 6% — 9 metrics — B4 Proposal, Proof, Trust & Ethics
R10 — Safeguarding & protected proof — 5% — 8 metrics — B4 Proposal, Proof, Trust & Ethics
R11 — Due diligence, finance & risk — 28% — 22 metrics — B5 Due Diligence, Operations & Financial Viability
R12 — Grant management & sustainability — 7% — 5 metrics — B6 Post-Award, Renewal & Adaptability

### 24 assessment areas/drivers
D01 Operating context and safety → R01
D02 Legal and receiving route → R01
D03 Funder market intelligence → R02
D04 Funder timing and access gates → R02
D05 Pipeline tracking and ownership → R03
D06 Go/no-go discipline and repair loop → R03
D07 Mandate and eligibility fit → R04
D08 Work design and grant-size fit → R04
D09 Competitive positioning → R05
D10 Value case and ROI → R05
D11 Access routes → R06
D12 Referrals and intermediaries → R06
D13 Relationship management → R07
D14 Leadership visibility → R07
D15 Application clarity and storytelling → R08
D16 Proposal coherence and budget/story alignment → R08
D17 Evidence readiness → R09
D18 Social proof and references → R09
D19 Safeguarding and ethics → R10
D20 Protected evidence and safe proof → R10
D21 Governance and controls → R11
D22 Finance, operations and risk → R11
D23 Sustainability and runway → R12
D24 Grant management and renewal → R12

## Technical stack
Build a boring, reliable, local-first production app:

- Backend: Python 3.11+ with FastAPI.
- Data processing: Python standard library + pandas allowed in the app code if useful, but decoding logic must be deterministic and tested.
- Spreadsheet imports: support `.csv` and `.xlsx`.
- Report DOCX: `docxtpl` or `python-docx` with explicit placeholder controls.
- PDF: LibreOffice headless conversion from populated DOCX to PDF.
- Frontend: simple React, server-rendered HTML, or FastAPI/Jinja; prioritise reliability over fancy UI.
- Storage: local encrypted or clearly separated `/data/uploads`, `/data/outputs`, `/data/logs` for pilot; design so storage can later move to S3-compatible storage.
- Database: SQLite for pilot; structure so PostgreSQL can replace it later.
- Packaging: Docker Compose with backend, app, and a LibreOffice/font-ready worker.

## App screens
1. Landing/upload screen
   - DOO U branded.
   - Calm, premium, clear language.
   - Upload single response, batch response, or LimeSurvey export.
   - Use demo data.
   - Choose Free Executive Report or Paid Full Report.

2. Report tier screen
   - Explain Free vs Full clearly.
   - Paid Full Report should feel worth buying.
   - Include manual unlock code placeholder and future Paystack/Stripe/WooCommerce hooks.
   - No real payment keys hard-coded.

3. Data review screen
   - Detect file type and response rows.
   - Show organisations detected.
   - Show decoded fields count, scored signals count, missing critical fields, protected evidence flags, unsafe route flags.
   - Show mapping version.

4. Processing screen
   - Show progress.
   - Process single or batch.
   - Fail clearly where required.

5. Results preview screen
   - Show overall readiness, band, top repair priorities, breakpoint stage, protected/unsafe flags.
   - Show downloads for DOCX/PDF only after QA gates pass.

6. Admin screen
   - Upload/update report template.
   - Upload/update product lock workbook.
   - Upload/update LSS.
   - Run test suite.
   - Export logs.
   - Clear local data.

## Decoder requirements
The decoder must support all likely LimeSurvey export shapes:

- Single-choice top-level fields: `R04_D07_Q02 = A03`.
- Multi-select fields: `R04_D07_Q01_SQ001 = Y`, blank otherwise.
- Matrix/document/route fields: `R10_D20_Q02_D1 = A05` or `R10_D20_Q02_SQ001 = A05`, depending on export format.
- Also support top-level semicolon summaries when present, e.g. `R04_D07_Q01 = SQ006;SQ010;SQ015`.
- Decode by locked question/subquestion codes first.
- Only use fuzzy question-text matching as a last fallback, and log it as a warning.

## Scoring engine
Implement deterministic scoring from the product lock workbook:

1. Decode answer values.
2. Map each answer to metric/driver/variable/report feed using the metric registry.
3. Calculate 24 driver scores.
4. Roll drivers into 12 variable scores.
5. Apply report-version variable weights.
6. Calculate weighted overall readiness.
7. Calculate 8 journey-stage scores.
8. Identify conversion breakpoint.
9. Rank repair priorities.
10. Identify strengths to lead with.
11. Classify document/evidence readiness.
12. Classify route readiness.
13. Flag protected evidence and unsafe routes.
14. Create manual-review queue.

## Score interpretation
0–20% = Major Barrier / Locked
21–40% = Conversion Risk / Fragile
41–60% = Light Friction / Emerging
61–80% = Low Barrier / Functional
81–100% = Strength / Strong

Lower readiness creates a higher conversion barrier. It never means the organisation is bad, weak, unserious, or undeserving.

## Hard fail gates
The app must refuse to generate a client-facing report if any of these are true:

- 0 scored survey signals decoded.
- Fewer than the required scored metrics decoded for selected tier.
- All 12 variables equal default placeholder 50%.
- Required organisation name is missing.
- Product lock workbook version is missing or mismatched.
- LSS version is missing or mismatched.
- Any report placeholder remains unresolved.
- Protected evidence is selected but free report would expose details.
- Unsafe route is selected and no manual-review flag is raised.
- DOCX export fails.
- PDF conversion fails.
- Verdana is not available for PDF conversion.
- PDF font check shows Verdana was substituted.
- Contents page promises sections not present in the final report.

## Report generation rules
### Free Executive Report
Include:
- branded summary/cover page;
- organisation name/context fields;
- overall readiness score and band;
- 12-variable snapshot;
- top 5 repair priorities;
- highest-weight repair area;
- main blockage;
- breakpoint stage;
- stop / verify / use now summary;
- 3 immediate next moves;
- invitation to buy Full Report or book DOO U review.

Exclude:
- full metric-level table;
- full 12 variable deep dives;
- full document/evidence triage;
- sensitive protected evidence details;
- full route analysis;
- appendix metric map.

### Paid Full Report
Use the Word template as master. Include:
- cover;
- contents;
- report-use pages;
- score logic;
- framework architecture;
- executive summary;
- conversion journey;
- variable scorecard;
- all 12 variable breakdown pages;
- metric-level tables per variable;
- document/evidence readiness;
- protected evidence guidance;
- route recommendations;
- synthesis;
- 30/60/90 plan;
- support/contact pages;
- appendix/metric map;
- internal audit outside the client-facing report.

## Font and brand QA
- Body font: Verdana.
- Headings: Aptos where supported.
- Brand colours: green #083F32 / #20352D / #214D3A / #2E6B4F; gold #C8A247; cream background.
- The PDF conversion environment must include Verdana.
- Add a QA command equivalent to:
  - `fc-match Verdana`
  - `pdffonts generated_report.pdf | grep -i verdana`
- If Verdana is not detected, fail the report.

## Batch requirements
For each batch:
- create batch ID;
- upload date;
- uploaded file name;
- number detected;
- number processed;
- number failed;
- number skipped;
- report tier per organisation;
- scoring map version;
- report template version;
- processing status.

For each organisation folder:
- Executive Report DOCX, if generated;
- Executive Report PDF, if generated;
- Full Report DOCX, if generated;
- Full Report PDF, if generated;
- score_summary.json;
- response_audit.json;
- missing_data_note.txt if relevant;
- protected_evidence_note.txt if relevant.

Create batch index CSV/XLSX with:
- organisation name;
- response status;
- overall readiness score;
- result band;
- top 3 repair priorities;
- highest-weight repair area;
- breakpoint stage;
- protected evidence flag;
- unsafe route flag;
- missing critical data flag;
- executive generated yes/no;
- full generated yes/no;
- file paths/download links;
- error notes.

## QA tests to implement
Create automated tests for:

1. Product lock validation:
   - 12 variables exist.
   - 24 drivers exist.
   - metric count totals 121.
   - variable weights total 100%.

2. Decoder:
   - single-choice answer codes decoded.
   - multi-select `Y` fields decoded.
   - matrix/document rows decoded.
   - top-level semicolon summaries decoded.
   - unknown fields logged but do not crash.

3. Scoring:
   - each of the five dummy pilot-client profiles produces a distinct result.
   - no profile returns 0 scored signals.
   - no profile returns all variables as placeholder 50%.
   - protected evidence profiles are flagged.
   - unsafe route profiles are flagged.

4. Report tier separation:
   - free report excludes protected evidence detail.
   - full report includes safe protected-evidence guidance.

5. Report QA:
   - no unresolved placeholders.
   - DOCX opens.
   - PDF exists.
   - Verdana detected.
   - contents sections match final report tier.

## Five dummy QA profiles that must pass
Use the uploaded fixtures:
- KLUG Route Repair QA.
- Sister Ghana Protected Proposal Review QA.
- TREAT Repressed Context Due-Diligence QA.
- Ubuntu Grassroots Action Collective Fiscal Host + Protected Evidence QA.
- Regional Feminist Route-Ready Intermediary Strong Systems QA.

Expected behaviour:
- They must not produce identical scores.
- At least two must trigger protected evidence.
- At least two must trigger unsafe/manual-review flags.
- At least one must produce a strong/functional result.
- At least one must produce fragile/locked repair priorities.
- Batch processing must produce five separate organisation folders and a batch index.

## Privacy/safety
- Local-first processing by default.
- Do not permanently store sensitive uploaded responses unless configured.
- Redact protected evidence in Free Report.
- Do not expose names, case details, locations, photos or sensitive evidence in summaries.
- Include consent/disclaimer language.

## Deliverables
Build and return:

1. Source code repository.
2. `README.md` with setup instructions for non-technical owner.
3. `.env.example` with no real keys.
4. Docker Compose file.
5. Admin instructions.
6. Test command instructions.
7. Sample processed outputs for the five test profiles.
8. Clear QA report showing pass/fail for all gates.

## Final acceptance criteria
The commercial app is accepted only when:

- The locked LSS imports into LimeSurvey.
- The app decodes exported responses by locked codes.
- Five dummy test profiles generate five different score patterns.
- Reports are blocked when scoring fails.
- Full Report uses the Word template, not a generic HTML redesign.
- DOCX is editable.
- PDF is polished and uses Verdana.
- Batch mode creates one folder per organisation.
- Protected evidence does not leak.
- Unsafe routes trigger manual review.
- No old G-variable labels appear.
- No client-facing technical words like backend, schema, debug, algorithm, raw code or mapping logic appear in the report.
- No shame language appears.

Build for reliability first, beauty second, automation third. A calm, correct report is more important than a flashy dashboard.
