# Report Renderer Specification - Ticket 06H

## Overview

Ticket 06H implements a Premium HTML/PDF Report Renderer that generates branded, deterministic, commercial-quality reports from `report_data.json`. This replaces the previous placeholder DOCX approach with a more reliable and visually consistent HTML-based rendering pipeline.

## Architecture

### Components

1. **report_content_builder.py**
   - Transforms `report_data.json` into structured content
   - Validates data integrity (decoded signal count, score spread)
   - Calculates diagnostic confidence scores
   - Labels all scores with descriptive text
   - Ensures no placeholder or generic content

2. **html_report_renderer.py**
   - Renders Jinja2 templates with structured content
   - Produces deterministic, branded HTML output
   - Applies custom Jinja2 filters for formatting
   - Validates template directory and file presence

3. **pdf_report_renderer.py**
   - Converts HTML to PDF using weasyprint
   - Gracefully handles missing dependencies
   - Returns explicit status (PDF_RENDERED, PDF_RENDER_ERROR, PDF_RENDER_NOT_ATTEMPTED)
   - Never crashes the report generation workflow

4. **batch_output.py** (updated)
   - Generates DOCX (legacy), HTML, and PDF reports
   - Tracks status for each output format independently
   - Returns structured metadata about generated files
   - Updates batch_quality_report.html with new status fields

5. **commercial_qa.py** (updated)
   - Separates DOCX assessment from HTML/PDF assessment
   - Maintains backward compatibility with legacy fields
   - Provides separate quality status for each format
   - Clearly documents why each format is PASS/WARNING/BLOCKED

## Report Content Structure

### 15 Sections

1. **Cover Page** - Organisation name, overall score, result band
2. **How to Read This Report** - Interpretation guide
3. **Diagnostic Confidence** - Signal count and confidence score
4. **Executive Summary** - Overall readiness band
5. **Funding Conversion Snapshot** - Journey stage progression
6. **12 Variable Scores** - Core readiness dimensions
7. **24 Assessment Area Scores** - Detailed sub-dimensions
8. **Application Journey Review** - Stage definitions
9. **Document & Evidence Readiness** - Evidence quality
10. **Top Repair Priorities** - Recommended focus areas
11. **Route Recommendation** - Funding conversion path
12. **30/60/90 Recommended Next Moves** - Phased action plan
13. **Manual Review & Safeguarding Notes** - Flags and cautions
14. **DOO U Support Options** - Available resources
15. **Contact** - Footer with details

## Data Flow

```
report_data.json
    ↓
build_report_content()
    ↓
structured_content (dict)
    ↓
render_html_report()
    ↓
report.html
    ↓
render_pdf_report()
    ↓
report_branded.pdf (or PDF_RENDER_ERROR)
```

## Validation Rules

### Before HTML Rendering

1. `decoded_scored_signal_count > 0` (no zero-signal reports)
2. `overall_score` is numeric and in range [0, 100]
3. `result_band` is non-empty
4. `variable_scores` dict is present with 12 entries
5. `assessment_area_scores` dict is present with 24 entries
6. At least one variable score is not 50% (meaningful spread)

### During Content Building

1. All score values are rounded to 2 decimal places
2. Variable/assessment area labels are populated from static map
3. Journey stage scores are labeled and ordered
4. Diagnostic confidence is calculated (0-100)
5. Manual review flags are preserved
6. Protection and unsafe route flags are included

### During HTML Rendering

1. Jinja2 environment is configured with auto-escaping
2. Custom filters are registered
3. Template inheritance is supported
4. No runtime template errors escape
5. Output is valid HTML5

### During PDF Rendering

1. If weasyprint unavailable: return PDF_RENDER_ERROR status
2. If weasyprint fails: return PDF_RENDER_ERROR with detail
3. If successful: create PDF file and return PDF_RENDERED
4. Never raise exceptions - always return status dict

## Brand Colours

- **Dark Green** (#20352D) - Primary text, headings
- **Deep Green** (#083F32) - Cover page, table headers
- **Soft Green** (#2E6B4F) - Secondary headings, highlights
- **Gold** (#C8A247) - Accents, borders, badges
- **Cream** (#F5F3F0) - Background, alternating rows

## Quality Gates

### HTML Report PASS Criteria

✓ `report_data.json` exists and is valid  
✓ Decoded signal count > 0  
✓ Variable scores populated and not all 50%  
✓ HTML file generated successfully  
✓ Organisation name appears in HTML  
✓ All 12 variables present  
✓ All 24 assessment areas present  
✓ Manual review requirements met  

### HTML Report BLOCKED When

✗ Decoded signal count = 0  
✗ Missing report_data.json  
✗ All variable scores are 50%  
✗ HTML rendering failed  
✗ Manual review required (still generated but marked for review)  

### PDF Report Status

- **PDF_RENDERED** - Successfully exported to PDF
- **PDF_RENDER_ERROR** - weasyprint failed or unavailable
- **PDF_RENDER_NOT_ATTEMPTED** - HTML rendering failed, no PDF attempt

## Testing Strategy

### Unit Tests

- `test_report_content_builder.py` - Content transformation
- `test_html_report_renderer.py` - HTML generation
- `test_pdf_report_renderer.py` - PDF export

### Integration Tests

- All 5 sample organisations generate HTML/PDF
- 5 organisations have unique reports (not all same score)
- Manual review flags visible
- Protected evidence handling
- Unsafe route visibility

### Coverage Requirements

1. All 5 sample organisations complete successfully
2. HTML includes organisation names
3. 12 variable scores present in HTML
4. 24 assessment area scores present in HTML
5. Top repair priorities included
6. Protected evidence not exposed in free reports
7. Manual review flags visible internally
8. Score diversity across 5 organisations
9. Commercial QA separates DOCX/HTML-PDF status
10. batch_quality_report.html shows status clearly

## Backward Compatibility

- DOCX generation continues but marked as BLOCKED in QA
- batch_output.py returns both legacy and new fields
- commercial_qa.py provides both old and new status fields
- Existing tests continue to pass
- No breaking changes to existing APIs

## Failure Modes & Graceful Degradation

### Missing Jinja2 Template

```
Error: "Template directory not found"
→ Raise HTMLReportRendererError with clear message
→ Batch processing stops (critical error)
```

### Missing weasyprint

```
Status: PDF_RENDER_ERROR
Message: "weasyprint not available; PDF rendering skipped"
→ HTML report generated successfully
→ pdf_path = None
→ PDF status tracked separately
→ Batch processing continues
```

### Zero Decoded Signals

```
Error: ReportContentBuilderError
Message: "Cannot render report: no decoded scored signals available"
→ Report marked BLOCKED
→ Batch processing continues for other organisations
```

### weasyprint Runtime Error

```
Status: PDF_RENDER_ERROR
Message: "{specific weasyprint error}"
→ HTML report remains valid
→ error_detail field populated
→ Batch processing continues
```

## Documentation Files

- **REPORT_RENDERER_SPEC.md** - This file
- **REPORT_DESIGN_TOKENS.md** - Colour scheme and typography
- **COMMERCIAL_QA_RELEASE_CRITERIA.md** - Quality gates and blocking criteria

## Future Enhancements

1. Free report variant (hide protected evidence)
2. Executive summary PDF (1-page digest)
3. Accessible PDF/A compliance
4. Multi-language support
5. Custom branding parameter
6. Interactive HTML (drill-down scores)
7. Report signing/verification
8. Automated distribution workflow
