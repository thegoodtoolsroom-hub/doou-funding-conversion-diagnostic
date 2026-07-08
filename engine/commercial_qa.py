from __future__ import annotations

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

    for org_dir in org_dirs:
        report_data_path = org_dir / "report_data.json"
        docx_path = org_dir / "report.docx"
        pdf_path = org_dir / "report.pdf"
        font_error_path = org_dir / "FONT_QA_ERROR.txt"

        report_data: dict[str, Any] = {}
        if report_data_path.exists():
            report_data = json.loads(report_data_path.read_text(encoding="utf-8"))

        docx_present = docx_path.exists()
        pdf_present = pdf_path.exists()
        font_error_present = font_error_path.exists()

        decoded_signal_count = int(report_data.get("decoded_scored_signal_count", 0) or 0)
        variable_scores = report_data.get("variable_scores", {}) or {}
        manual_review_flags = report_data.get("manual_review_flags", []) or []
        scores_not_all_fifty = bool(variable_scores) and any(value != 50 for value in variable_scores.values())
        manual_review_required = bool(manual_review_flags) and any("manual review" in flag.lower() for flag in manual_review_flags)

        docx_text = ""
        if docx_present:
            try:
                from docx import Document

                doc = Document(str(docx_path))
                docx_text = "\n".join(paragraph.text for paragraph in doc.paragraphs if paragraph.text).lower()
            except Exception:
                docx_text = ""

        template_quality_blocked = False
        placeholder_generic_content_blocked = False
        font_qa_blocked = False
        font_qa_status = "FONT_QA_OK"
        status_message = "Structurally generated and commercially safe."

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

        commercial_quality_status = "PASS"
        blocking_reasons: list[str] = []
        if template_quality_blocked:
            blocking_reasons.append(
                "DOCX output is structurally generated but not yet final commercial quality because it is not section-injected into the master report template."
            )
        if placeholder_generic_content_blocked:
            blocking_reasons.append(
                "Generated content is placeholder/generic rather than final commercial-quality client report content."
            )
        if font_qa_blocked:
            blocking_reasons.append("PDF font QA failed or was not verified as Verdana.")
        if not report_data_path.exists():
            blocking_reasons.append("Missing report_data.json.")
        if decoded_signal_count <= 0:
            blocking_reasons.append("No decoded scored signals were available.")
        if not variable_scores:
            blocking_reasons.append("Missing variable score payload.")
        if not scores_not_all_fifty:
            blocking_reasons.append("All variables are 50%, which is not a meaningful commercial-quality spread.")
        if manual_review_required:
            blocking_reasons.append("Manual review required for protected or unsafe route content.")

        if blocking_reasons:
            commercial_quality_status = "BLOCKED"
            status_message = " ".join(blocking_reasons[:2])
        elif not docx_present or not pdf_present:
            commercial_quality_status = "WARNING"
            status_message = "Structurally generated but incomplete for commercial use."
        else:
            commercial_quality_status = "PASS"
            status_message = "Structurally generated and commercially safe."

        results.append(
            {
                "organisation_name": report_data.get("organisation_profile", {}).get("name", org_dir.name),
                "organisation_slug": org_dir.name,
                "report_data_path": str(report_data_path),
                "docx_present": docx_present,
                "pdf_present": pdf_present,
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
            f"<td>{'Yes' if item['structurally_generated'] else 'No'}</td>"
            f"<td>{'Yes' if item['docx_present'] and item['pdf_present'] else 'No'}</td>"
            f"<td>{item['commercial_quality_status']}</td>"
            f"<td>{item['font_qa_status']}</td>"
            f"<td>{item['status_message']}</td>"
            f"<td>{'Yes' if item['template_quality_blocked'] else 'No'}</td>"
            f"<td>{'Yes' if item['placeholder_generic_content_blocked'] else 'No'}</td>"
            f"<td>{'Yes' if item['font_qa_blocked'] else 'No'}</td>"
            "</tr>"
        )

    html = f"""<!DOCTYPE html>
<html lang=\"en\">
<head><meta charset=\"utf-8\"><title>Commercial quality report</title></head>
<body>
<h1>Commercial quality report</h1>
<p>This report marks whether each organisation batch output is structurally generated, commercially usable, or blocked for template quality, placeholder/generic content, or font QA.</p>
<table>
<tr><th>Organisation</th><th>Structurally generated</th><th>Artifacts present</th><th>Commercial quality status</th><th>Font QA status</th><th>Status message</th><th>Template quality blocked</th><th>Placeholder/generic blocked</th><th>Font QA blocked</th></tr>
{''.join(rows)}
</table>
</body>
</html>"""
    (root / "batch_quality_report.html").write_text(html, encoding="utf-8")
    return html


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
