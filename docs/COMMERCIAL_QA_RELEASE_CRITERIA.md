# Commercial QA Release Criteria - Ticket 06H

## Executive Summary

This document defines the quality gates and blocking criteria for Ticket 06H HTML/PDF Report Renderer implementation. It separates the assessment of DOCX (legacy) from HTML/PDF (primary) formats, ensuring transparency about which formats are production-ready.

## Quality Gates Overview

### Report Format Comparison

| Criterion | DOCX (Legacy) | HTML/PDF (Primary) |
|-----------|---------------|-------------------|
| Template Injection | Not attempted | N/A (deterministic HTML) |
| Placeholder Content | Yes | No (data-driven only) |
| Commercial Ready | BLOCKED | Conditional PASS |
| Recommended Use | Internal only | External distribution |
| Stability | Low | High (deterministic) |

## DOCX Format Assessment

### Current Status: BLOCKED

The DOCX format is currently BLOCKED from commercial distribution due to:

1. **No Section Injection:** The DOCX is a placeholder copy of the master template without dynamic content injection
2. **Generic Content:** Placeholder text appended to the document
3. **No Real Data Integration:** Organisation data is not properly injected into template sections
4. **Template Structure Not Preserved:** The output is not visually consistent with the master design

### DOCX Blocking Reasons

```
BLOCKED: DOCX output is structurally generated but not yet final 
commercial quality because it is not section-injected into the 
master report template.

BLOCKED: Generated DOCX content is placeholder/generic rather than 
final commercial-quality client report content.

BLOCKED: DOCX PDF font QA failed or was not verified as Verdana.
```

### DOCX Future Path (Ticket 06S - Not This Session)

A future ticket (Ticket 06S) may implement real Word template section injection to move DOCX to PASS status. Until then:

- DOCX may remain in outputs for backward compatibility
- DOCX status field clearly shows BLOCKED
- Do not distribute DOCX to external stakeholders
- Use HTML/PDF as primary external format

## HTML/PDF Format Assessment

### Primary Status: PASS (with qualifications)

HTML/PDF reports are production-ready when:

✓ All data validation rules pass  
✓ HTML renders without errors  
✓ Organisation-specific content is present  
✓ All required report sections are included  
✓ Manual review requirements are satisfied  

### HTML/PDF Quality Criteria

#### Must Pass (BLOCKED if failed)

1. **Data Integrity**
   - `report_data.json` exists and is valid JSON
   - `decoded_scored_signal_count > 0` (at least one signal decoded)
   - Numeric scores are in valid range [0, 100]
   - `overall_score` is not NULL or invalid

2. **Content Diversity**
   - Variable scores are NOT all 50% (meaningful spread required)
   - At least 2 variables have score variance >= 10%
   - Visual indication that report is organisation-specific

3. **Report Completeness**
   - HTML file successfully generated
   - File size > 1KB (not empty/malformed)
   - All 12 variable codes present (R01-R12)
   - All 24 assessment area codes present (D01-D24)
   - Organisation name appears in document

4. **Rendering Robustness**
   - No Jinja2 template errors
   - No missing required data fields
   - No encoding/character issues
   - Valid HTML5 output

#### May Pass (WARNING if issues)

5. **PDF Export Status**
   - If `weasyprint` available: PDF file created (PASS)
   - If `weasyprint` unavailable: PDF_RENDER_ERROR returned (WARNING, not blocked)
   - If weasyprint fails: Clear error message provided (WARNING, not blocked)
   - HTML always generated regardless of PDF status

6. **Safeguarding Compliance**
   - Manual review flags clearly documented
   - Protected evidence visibility respected
   - Unsafe route assessment included
   - No inadvertent exposure of restricted information

### HTML/PDF Blocking Criteria

Report is BLOCKED (cannot be generated) if:

```
BLOCKED: No decoded scored signals were available.
         → Cannot render report without any response data

BLOCKED: Missing report_data.json.
         → Cannot generate report without source data

BLOCKED: Missing variable score payload.
         → Cannot populate core scoring dimensions

BLOCKED: All variables are 50%, which is not a meaningful 
         commercial-quality spread.
         → Not organisation-specific (possible error condition)

BLOCKED: Manual review required for protected or unsafe route 
         content.
         → Report flagged for human review before distribution
```

### HTML/PDF Warning Criteria

Report is WARNING (generated but with caution) if:

```
WARNING: HTML generated but PDF may not be available.
         → HTML is valid; PDF export failed or skipped

WARNING: weasyprint not available; PDF rendering skipped.
         → HTML report is complete; PDF export not possible
         → HTML file is production-ready
         → PDF status: PDF_RENDER_ERROR (acceptable)
```

## Commercial Quality Status Values

### For HTML/PDF Reports

| Status | Definition | Action | Commercial Use |
|--------|-----------|--------|-----------------|
| PASS | All criteria met; report ready | Approve for use | Yes, recommended |
| WARNING | Report generated; PDF may be unavailable | Review PDF status | Conditional (HTML OK) |
| BLOCKED | Report cannot be generated safely | Investigate error | No, do not distribute |

### For DOCX Reports (Legacy)

| Status | Definition | Action | Commercial Use |
|--------|-----------|--------|-----------------|
| PASS | (Unreachable) | N/A | No |
| WARNING | (Unreachable) | N/A | No |
| BLOCKED | Current state (all reports) | Do not use | No, always blocked |

## Release Checklist

### Before Deploying Ticket 06H to Production

- [ ] All 5 sample organisations generate HTML reports successfully
- [ ] HTML reports are visually distinct (not identical content)
- [ ] All 12 variables present in each report
- [ ] All 24 assessment areas present in each report
- [ ] Organisation names correctly appear in reports
- [ ] Top repair priorities populated and relevant
- [ ] Protected evidence handling works correctly
- [ ] Unsafe route flags display correctly
- [ ] Manual review requirements respected
- [ ] Overall scores differ across 5 organisations
- [ ] batch_quality_report.html shows HTML/PDF status clearly
- [ ] batch_quality_report.html shows DOCX status as BLOCKED
- [ ] Separate DOCX/HTML-PDF quality tracking confirmed
- [ ] All new tests pass (test_report_content_builder, test_html_report_renderer, test_pdf_report_renderer)
- [ ] Existing tests continue to pass (29 tests)
- [ ] PDF graceful degradation works (no crashes if weasyprint unavailable)
- [ ] Documentation is complete and accurate

### Test Requirements

```bash
make test          # Must pass 29+ tests, including new test modules
make generate-sample  # Must complete without errors
```

### Manual Verification

1. Open `outputs/sample_batch/batch_quality_report.html`
2. Verify table shows:
   - DOCX Status: BLOCKED (all organisations)
   - HTML/PDF Status: PASS or WARNING (based on PDF availability)
   - Status messages clearly explain each state

3. Sample reports spot-check:
   - Pick one organisation
   - Open `report.html` in browser
   - Verify: name, scores, sections, colours
   - Check PDF file exists (or verify PDF_RENDER_ERROR if weasyprint unavailable)

## Error Scenarios & Responses

### Scenario 1: weasyprint Not Available

**Observed:** `pip freeze | grep weasyprint` shows empty

**Expected Behaviour:**
- HTML reports generate successfully ✓
- PDF_RENDER_ERROR returned for each organisation ✓
- batch_quality_report.html shows PDF status: PDF_RENDER_ERROR ✓
- Tests pass (checking for error status, not file presence) ✓
- No crashes or exceptions ✓

**Resolution:** Optional install: `pip install weasyprint` for PDF support

### Scenario 2: Zero Decoded Signals

**Observed:** Report data has `decoded_scored_signal_count = 0`

**Expected Behaviour:**
- ReportContentBuilderError raised with clear message ✓
- Organisation skipped (batch continues) ✓
- batch_quality_report.html shows BLOCKED status ✓
- Error message: "Cannot render report: no decoded scored signals" ✓

**Resolution:** Investigate decoding step; verify response data is present

### Scenario 3: All Scores Are 50%

**Observed:** Every variable score exactly 50%

**Expected Behaviour:**
- Report is BLOCKED ✓
- Batch processing continues ✓
- Status message: "All variables are 50%, not meaningful spread" ✓
- Likely indicates data corruption or placeholder input ✓

**Resolution:** Investigate scoring engine; check input data quality

### Scenario 4: Jinja2 Template Not Found

**Observed:** `templates/report_html/report.html` doesn't exist

**Expected Behaviour:**
- HTMLReportRendererError raised immediately ✓
- Batch processing stops (critical error) ✓
- Error message: "Template directory not found" ✓
- All reports marked BLOCKED ✓

**Resolution:** Verify template directory structure; re-run deployment

## Backward Compatibility

### Existing Tests

All existing 29 tests must continue to pass:
- `test_scaffold.py` ✓
- `test_product_lock_loader.py` ✓
- `test_limesurvey_decoder.py` ✓
- `test_scoring_engine.py` ✓
- `test_report_data_builder.py` ✓
- `test_commercial_qa.py` ✓
- `test_batch_output.py` (updated with new assertions)

### Data Format

- `report_data.json` structure unchanged ✓
- `batch_index.csv` structure unchanged ✓
- `response_audit.json` structure unchanged ✓
- New fields added to generated batch metadata (non-breaking) ✓

### API Contract

- `generate_batch_outputs()` returns enhanced dict (backward compatible) ✓
- `inspect_batch_output()` adds new fields (backward compatible) ✓
- `render_batch_quality_report()` now includes HTML/PDF status (enhanced) ✓

## Handover Criteria

### For Next Session

- [ ] Ticket 06H complete and tested
- [ ] All 29 existing tests pass + new tests (60+ total expected)
- [ ] make test passes cleanly
- [ ] make generate-sample completes without errors
- [ ] batch_quality_report.html shows correct HTML/PDF/DOCX status
- [ ] No crashes or uncaught exceptions in error scenarios
- [ ] Documentation complete (REPORT_RENDERER_SPEC.md, REPORT_DESIGN_TOKENS.md, this file)
- [ ] Ready for Ticket 07 (Web App) - do not start until these criteria met

### Known Limitations (Acceptable)

1. DOCX format remains BLOCKED pending Ticket 06S
2. PDF requires optional weasyprint package for full support
3. Free report variant not yet implemented (future enhancement)
4. No report signing or verification yet (future enhancement)
5. Single language (English) only (future: multi-language)

## Contact & Escalation

If quality criteria are not met:

1. **Assertion Failure:** Check test output for specific error
2. **Missing Dependencies:** Install: `pip install weasyprint jinja2`
3. **Template Errors:** Verify `templates/report_html/report.html` exists
4. **Data Errors:** Review sample data in `test_data/BATCH_04_TEST_DATA_UPLOAD_FOURTH/`
5. **Unclear Status:** Review commercial_qa.py `inspect_batch_output()` logic

---

**Document Version:** 1.0  
**Last Updated:** 2026-07-08  
**Status:** Active for Ticket 06H Release  
**Next Review:** After Ticket 06H production deployment  
