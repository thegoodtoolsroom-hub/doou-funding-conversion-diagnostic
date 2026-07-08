# Ticket 06S — Real Word Template Section Injection Plan

## 1. What Ticket 06S must solve

Ticket 06S must replace the current placeholder DOCX output with a report that is genuinely built from the master Word template rather than merely copied or supplemented with generic text.

The goal is to make the generated DOCX look like a real report artifact produced from the approved template, with actual report sections populated from the engine data.

This ticket must not pretend commercial readiness. If the template cannot be section-injected safely, the output must remain blocked by commercial QA.

## 2. Master Word template file to inspect

Inspect the master Word template in:

- templates/BATCH_03_REPORT_TEMPLATE_MASTER_UPLOAD_THIRD/

The plan should identify the actual .docx file in that folder and review it for:
- section structure,
- heading hierarchy,
- reusable content blocks,
- placeholders or content controls,
- styling details that must be preserved.

## 3. Dynamic report fields that need to be inserted

The generated report must populate the following dynamic values from the existing engine output:
- organisation name
- overall score
- result band
- variable scores
- assessment-area scores
- top repair priorities
- manual review flags
- protected evidence / unsafe route visibility decisions
- any report summary and contextual narrative that is already available in report_data.json

The insertion should be driven by the existing report_data bundle rather than by hard-coded generic prose.

## 4. Placeholders/content controls that may be needed

The template should be reviewed for any of the following:
- plain-text placeholders such as {{organisation_name}}
- custom content controls
- bookmarks
- text form fields
- repeating sections or tables for scores and priorities
- named placeholders for summary sections

If the template has no obvious placeholders, the implementation should still use a safe, explicit blocker approach rather than appending generic content.

## 5. How to avoid appending generic text

The generator must not simply append paragraphs like “This placeholder report preserves the template...” to the end of the document.

Instead:
- populate the actual template sections,
- insert values into the intended document locations,
- preserve the template layout and typography,
- avoid creating a document that looks like a generic text dump.

If the template does not yet support structured injection, the ticket should explicitly keep the output blocked rather than pretending it is final-quality.

## 6. How to preserve the Word design

The implementation must preserve the master design by:
- keeping the existing Word styles intact,
- reusing the template’s formatting and layout,
- avoiding changes to the master template itself unless explicitly required,
- inserting content into existing sections rather than replacing the whole document structure.

The generated document should remain visually consistent with the approved Word template.

## 7. Tests that must pass before commercial QA can move from BLOCKED to WARNING or PASS

Before commercial QA can move out of BLOCKED, the following must be demonstrated by tests:
- a generated DOCX is produced from the master template rather than a generic placeholder document,
- the expected report sections are populated from report_data,
- dynamic fields are inserted into the intended locations,
- the document still preserves the template’s Word design and structure,
- commercial QA no longer flags the DOCX as template-quality blocked,
- PDF font QA is either verified as Verdana or clearly reported as a separate commercial blocker.

These tests should verify both the presence of inserted data and the absence of placeholder/generic content patterns.

## 8. Why Ticket 07 must wait

Ticket 07 must wait because the batch output is still not commercially safe.

Until real template section injection is implemented and validated:
- the DOCX output remains blocked by commercial QA,
- the report cannot be honestly presented as final-quality client output,
- the product would still be releasing placeholder-like content rather than a trusted report artifact.

Ticket 07 should only begin after Ticket 06S proves the generated reports are structurally and commercially safer than the current placeholder state.
