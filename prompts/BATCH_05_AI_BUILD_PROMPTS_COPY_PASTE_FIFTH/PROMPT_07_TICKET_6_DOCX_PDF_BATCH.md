Ticket 6: Build DOCX/PDF generation and batch output.

Use the Word report template in templates/ as the master design.
Do not recreate the paid report from HTML.

For each organisation:
- create a folder
- create report_data.json
- create editable DOCX
- create PDF
- create response audit
- create manual review note if needed

For the batch:
- create batch_index.csv
- create batch_index.xlsx
- create batch_quality_report.html

QA checks:
- no unresolved placeholders
- no all-50 default reports
- no zero-signal reports
- PDF exists
- Verdana appears in PDF or clear font failure appears

Run tests.
