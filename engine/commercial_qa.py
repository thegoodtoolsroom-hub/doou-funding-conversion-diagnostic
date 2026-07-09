from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


_PLACEHOLDER_TOKENS = (
    "placeholder",
    "generic",
    "automated section injection",
    "current limitation",
)


def inspect_batch_output(batch_root: str | Path) -> list[dict[str, Any]]:
    root = Path(batch_root)
    org_dirs = sorted([path for path in root.iterdir() if path.is_dir()])
    results: list[dict[str, Any]] = []
    render_statuses = _read_batch_index_statuses(root)

    for org_dir in org_dirs:
        report_data_path = org_dir / "report_data.json"
        docx_path = org_dir / "report.docx"
        html_path = org_dir / "report.html"
        pdf_path = _find_pdf_path(org_dir)
        font_error_path = org_dir / "FONT_QA_ERROR.txt"

        report_data: dict[str, Any] = {}
        if report_data_path.exists():
            report_data = json.loads(report_data_path.read_text(encoding="utf-8"))

        docx_present = docx_path.exists()
        html_present = html_path.exists()
        pdf_present = pdf_path.exists()
        font_error_present = font_error_path.exists()
        render_status = render_statuses.get(org_dir.name, {})
        html_status = render_status.get("html_status") or ("HTML_RENDERED" if html_present else "HTML_RENDER_ERROR")
        pdf_status = render_status.get("pdf_status") or ("PDF_RENDERED" if pdf_present else "PDF_RENDER_ERROR")

        decoded_signal_count = int(report_data.get("decoded_scored_signal_count", 0) or 0)
        variable_scores = report_data.get("variable_scores", {}) or {}
        manual_review_flags = report_data.get("manual_review_flags", []) or []
        scores_not_all_fifty = bool(variable_scores) and any(value != 50 for value in variable_scores.values())
        manual_review_required = any(_is_actionable_manual_review_flag(flag) for flag in manual_review_flags)

        docx_text = ""
        if docx_present:
            try:
                from docx import Document

                doc = Document(str(docx_path))
                docx_text = "\n".join(paragraph.text for paragraph in doc.paragraphs if paragraph.text).lower()
            except Exception:
                docx_text = ""

        # DOCX Assessment (legacy format, may be blocked)
        template_quality_blocked = False
        placeholder_generic_content_blocked = False
        font_qa_blocked = False
        font_qa_status = "FONT_QA_OK"
        docx_status_message = "Structurally generated and commercially safe."
        docx_quality_status = "PASS"

        if docx_present:
            placeholder_generic_content_blocked = _looks_placeholder_content(docx_text)
            template_quality_blocked = not _is_template_injected(docx_text) or placeholder_generic_content_blocked
        else:
            template_quality_blocked = True
            placeholder_generic_content_blocked = True

        if font_error_present:
            font_qa_status = "FONT_QA_ERROR"
            font_qa_blocked = True
        elif pdf_present:
            font_qa_status = "FONT_QA_BLOCKED"
            font_qa_blocked = True
        else:
            font_qa_status = "FONT_QA_BLOCKED"
            font_qa_blocked = True

        blocking_reasons: list[str] = []
        if template_quality_blocked:
            blocking_reasons.append(
                "DOCX output is structurally generated but not yet final commercial quality because it is not section-injected into the master report template."
            )
        if placeholder_generic_content_blocked:
            blocking_reasons.append(
                "Generated DOCX content is placeholder/generic rather than final commercial-quality client report content."
            )
        if font_qa_blocked:
            blocking_reasons.append("DOCX PDF font QA failed or was not verified as Verdana.")

        if blocking_reasons:
            docx_quality_status = "BLOCKED"
            docx_status_message = " ".join(blocking_reasons[:2])
        elif not docx_present:
            docx_quality_status = "WARNING"
            docx_status_message = "DOCX artifact not present."
        else:
            docx_quality_status = "PASS"
            docx_status_message = "DOCX structurally generated and commercially safe."

        # HTML/PDF Assessment (new primary format)
        html_pdf_quality_status = "PASS"
        html_pdf_status_message = "HTML/PDF report successfully generated."
        html_pdf_blocking_reasons: list[str] = []

        if not report_data_path.exists():
            html_pdf_blocking_reasons.append("Missing report_data.json.")
        if decoded_signal_count <= 0:
            html_pdf_blocking_reasons.append("No decoded scored signals were available.")
        if not variable_scores:
            html_pdf_blocking_reasons.append("Missing variable score payload.")
        if not scores_not_all_fifty:
            html_pdf_blocking_reasons.append("All variables are 50%, which is not a meaningful commercial-quality spread.")
        if manual_review_required:
            html_pdf_blocking_reasons.append("Manual review required for protected or unsafe route content.")

        if not html_present:
            html_pdf_blocking_reasons.append("HTML report was not generated.")
        
        if html_pdf_blocking_reasons:
            html_pdf_quality_status = "BLOCKED"
            html_pdf_status_message = " ".join(html_pdf_blocking_reasons[:2])
        elif not html_present or not pdf_present:
            html_pdf_quality_status = "WARNING"
            html_pdf_status_message = f"HTML generated; PDF status is {pdf_status}."
        else:
            html_pdf_quality_status = "PASS"
            html_pdf_status_message = "HTML/PDF report successfully generated and commercially safe."

        commercial_quality_status = _aggregate_quality_status(docx_quality_status, html_pdf_quality_status)
        status_message = _aggregate_status_message(
            docx_quality_status,
            html_pdf_quality_status,
            docx_status_message,
            html_pdf_status_message,
        )

        results.append(
            {
                "organisation_name": report_data.get("organisation_profile", {}).get("name", org_dir.name),
                "organisation_slug": org_dir.name,
                "report_data_path": str(report_data_path),
                "docx_present": docx_present,
                "html_present": html_present,
                "pdf_present": pdf_present,
                "pdf_path": str(pdf_path),
                "html_status": html_status,
                "pdf_status": pdf_status,
                "font_error_present": font_error_present,
                "docx_text_preview": _preview_text(docx_text),
                "decoded_scored_signal_count": decoded_signal_count,
                "variable_scores": variable_scores,
                "manual_review_flags": manual_review_flags,
                "scores_not_all_fifty": scores_not_all_fifty,
                "manual_review_required": manual_review_required,
                "template_quality_blocked": template_quality_blocked,
                "placeholder_generic_content_blocked": placeholder_generic_content_blocked,
                "font_qa_blocked": font_qa_blocked,
                "font_qa_status": font_qa_status,
                # DOCX quality assessment
                "docx_quality_status": docx_quality_status,
                "docx_status_message": docx_status_message,
                # HTML/PDF quality assessment
                "html_pdf_quality_status": html_pdf_quality_status,
                "html_pdf_status_message": html_pdf_status_message,
                # Legacy fields for backward compatibility. These remain strict and
                # blocked if either tracked format is blocked.
                "overall_commercial_quality_status": commercial_quality_status,
                "commercial_quality_status": commercial_quality_status,
                "status_message": status_message,
                "structurally_generated": True,
            }
        )

    return results


def render_batch_quality_report(batch_root: str | Path, results: list[dict[str, Any]] | None = None) -> str:
    root = Path(batch_root)
    if results is None:
        results = inspect_batch_output(root)

    rows = []
    for item in results:
        rows.append(
            "<tr>"
            f"<td>{item['organisation_name']}</td>"
            f"<td>{item.get('docx_quality_status', 'UNKNOWN')}</td>"
            f"<td>{item.get('html_status', 'UNKNOWN')}</td>"
            f"<td>{item.get('pdf_status', 'UNKNOWN')}</td>"
            f"<td>{item.get('html_pdf_quality_status', 'UNKNOWN')}</td>"
            f"<td style='font-size: 0.9em;'>{item.get('html_pdf_status_message', 'N/A')[:100]}</td>"
            "</tr>"
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Commercial Quality Report - Ticket 06H HTML/PDF Report Renderer</title>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #F5F3F0; padding: 20px; }}
        h1 {{ color: #20352D; border-bottom: 3px solid #C8A247; padding-bottom: 10px; }}
        h2 {{ color: #2E6B4F; }}
        p {{ color: #666; line-height: 1.6; }}
        table {{ width: 100%; border-collapse: collapse; background-color: white; margin-top: 20px; }}
        th {{ background-color: #083F32; color: white; padding: 12px; text-align: left; font-weight: 600; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #E0E0E0; }}
        tr:nth-child(even) {{ background-color: #F5F3F0; }}
        tr:hover {{ background-color: #FFFDE7; }}
        .status-pass {{ background-color: #E8F5E9; color: #2E7D32; font-weight: 600; }}
        .status-blocked {{ background-color: #FFEBEE; color: #C62828; font-weight: 600; }}
        .status-warning {{ background-color: #FFF3E0; color: #E65100; font-weight: 600; }}
        .docx-section {{ background-color: #F3F3F3; margin-top: 30px; padding: 15px; border-radius: 4px; }}
        .html-pdf-section {{ background-color: #E8F5E9; margin-top: 30px; padding: 15px; border-radius: 4px; }}
    </style>
</head>
<body>
<h1>Commercial Quality Report - Ticket 06H HTML/PDF Report Renderer</h1>
<p>Assessment of report generation quality across HTML/PDF (primary) and DOCX (legacy) formats.</p>

<h2>Report Generation Status Summary</h2>
<p><strong>Primary Format:</strong> HTML with PDF export (branded, deterministic, commercial-quality)</p>
<p><strong>Legacy Format:</strong> DOCX (placeholder, not section-injected)</p>

<table>
<tr>
    <th>Organisation</th>
    <th>DOCX Status</th>
    <th>HTML Render</th>
    <th>PDF Render</th>
    <th>HTML/PDF Quality Status</th>
    <th>Status Message</th>
</tr>
{''.join(rows)}
</table>

<div class="docx-section">
    <h2>DOCX (Legacy) Format Assessment</h2>
    <p><strong>Status:</strong> The DOCX format remains a placeholder implementation and is not section-injected into the master Word template. This format may be kept for backward compatibility but is NOT recommended for commercial distribution.</p>
    <p><strong>Recommendation:</strong> Use HTML/PDF format for all commercial reporting and funding conversion applications.</p>
</div>

<div class="html-pdf-section">
    <h2>HTML/PDF (Primary) Format Assessment</h2>
    <p><strong>Status:</strong> The HTML/PDF format is deterministic, branded with DOO U colours, and suitable for commercial distribution. This is the primary recommended format for funding conversion reports.</p>
    <p><strong>Quality Criteria:</strong> HTML/PDF reports meet commercial quality standards when:</p>
    <ul>
        <li>report_data.json is present and valid</li>
        <li>Decoded signal count is greater than 0</li>
        <li>Variable scores are populated and not all 50%</li>
        <li>Manual review requirements are met</li>
        <li>HTML report renders successfully</li>
        <li>PDF export is attempted (may fail gracefully if weasyprint unavailable)</li>
    </ul>
    <p><strong>Note:</strong> If PDF export fails due to missing weasyprint package, the HTML report is still generated and marked as valid. The PDF_RENDER_ERROR status indicates the specific limitation.</p>
</div>

</body>
</html>"""
    (root / "batch_quality_report.html").write_text(html, encoding="utf-8")
    return html


def _read_batch_index_statuses(root: Path) -> dict[str, dict[str, str]]:
    index_path = root / "batch_index.csv"
    if not index_path.exists():
        return {}

    statuses: dict[str, dict[str, str]] = {}
    with index_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            slug = row.get("organisation_slug")
            if slug:
                statuses[slug] = {key: value for key, value in row.items() if value}
    return statuses


def _find_pdf_path(org_dir: Path) -> Path:
    for name in ("report_branded.pdf", "report.pdf"):
        candidate = org_dir / name
        if candidate.exists():
            return candidate
    return org_dir / "report_branded.pdf"


def _is_actionable_manual_review_flag(flag: Any) -> bool:
    lowered = str(flag).strip().lower()
    if not lowered or lowered == "no manual review required":
        return False
    return any(
        token in lowered
        for token in ("manual review", "requires review", "protected evidence", "unsafe route")
    )


def _aggregate_quality_status(docx_status: str, html_pdf_status: str) -> str:
    if "BLOCKED" in {docx_status, html_pdf_status}:
        return "BLOCKED"
    if "WARNING" in {docx_status, html_pdf_status}:
        return "WARNING"
    return "PASS"


def _aggregate_status_message(
    docx_status: str,
    html_pdf_status: str,
    docx_message: str,
    html_pdf_message: str,
) -> str:
    if docx_status == "BLOCKED":
        return docx_message
    if html_pdf_status != "PASS":
        return html_pdf_message
    return html_pdf_message


def _is_template_injected(docx_text: str) -> bool:
    lowered = docx_text.lower()
    if not lowered:
        return False
    if any(token in lowered for token in _PLACEHOLDER_TOKENS):
        return False
    return "section" in lowered and "template" in lowered


def _looks_placeholder_content(docx_text: str) -> bool:
    lowered = docx_text.lower()
    return any(token in lowered for token in _PLACEHOLDER_TOKENS)


def _preview_text(text: str, limit: int = 120) -> str:
    return text[:limit].replace("\n", " ") if text else ""
