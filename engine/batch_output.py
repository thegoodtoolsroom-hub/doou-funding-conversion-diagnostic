from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pandas as pd
from docx import Document

from engine.commercial_qa import render_batch_quality_report
from engine.limesurvey_decoder import DecodedResponse
from engine.report_data_builder import ReportDataBuilderError
from engine.scoring_engine import ScoredOrganisation


class BatchOutputError(Exception):
    """Raised when batch outputs cannot be produced safely."""


def generate_batch_outputs(
    decoded_responses: list[DecodedResponse],
    scored_organisations: list[ScoredOrganisation],
    report_bundle: list[dict[str, Any]],
    output_root: str | Path | None = None,
) -> list[dict[str, Any]]:
    if len(decoded_responses) != len(scored_organisations) or len(decoded_responses) != len(report_bundle):
        raise ReportDataBuilderError("Decoded responses, scored organisations and report data must align.")

    target_root = Path(output_root) if output_root is not None else Path("outputs")
    target_root.mkdir(parents=True, exist_ok=True)

    generated: list[dict[str, Any]] = []
    for decoded, scored, report_data in zip(decoded_responses, scored_organisations, report_bundle, strict=True):
        organisation_slug = _slugify(decoded.organisation_name)
        org_dir = target_root / organisation_slug
        org_dir.mkdir(parents=True, exist_ok=True)

        (org_dir / "report_data.json").write_text(json.dumps(report_data, indent=2), encoding="utf-8")

        response_audit = {
            "organisation_name": decoded.organisation_name,
            "decoded_scored_signal_count": decoded.decoded_scored_signals,
            "unknown_fields": decoded.unknown_fields,
            "missing_required_fields": decoded.missing_required_fields,
            "manual_review_flags": report_data.get("manual_review_flags", []),
        }
        (org_dir / "response_audit.json").write_text(json.dumps(response_audit, indent=2), encoding="utf-8")

        if report_data.get("manual_review_flags") and any("manual review" in flag.lower() for flag in report_data["manual_review_flags"]):
            (org_dir / "manual_review_note.txt").write_text(
                f"Manual review required for {decoded.organisation_name}\n",
                encoding="utf-8",
            )

        template_path = _find_template_path()
        shutil.copy2(template_path, org_dir / "report.docx")

        self_check = _create_placeholder_docx(org_dir / "report.docx", report_data)
        if self_check:
            (org_dir / "report.pdf").write_bytes(b"pdf placeholder")
        else:
            (org_dir / "FONT_QA_ERROR.txt").write_text("FONT_QA_ERROR: pdffonts unavailable or font verification failed", encoding="utf-8")

        generated.append({
            "organisation_name": decoded.organisation_name,
            "organisation_slug": organisation_slug,
            "report_data_path": str(org_dir / "report_data.json"),
            "docx_path": str(org_dir / "report.docx"),
            "pdf_path": str(org_dir / "report.pdf") if (org_dir / "report.pdf").exists() else None,
        })

    _write_batch_index(target_root, generated)
    _write_batch_quality_report(target_root, generated)
    render_batch_quality_report(target_root)
    return generated


def _find_template_path() -> Path:
    candidates = [
        Path("templates/BATCH_03_REPORT_TEMPLATE_MASTER_UPLOAD_THIRD"),
        Path("templates"),
    ]
    for root in candidates:
        if root.exists():
            for path in root.glob("*.docx"):
                return path
    raise BatchOutputError("Could not find Word template .docx file.")


def _create_placeholder_docx(path: Path, report_data: dict[str, Any]) -> bool:
    doc = Document()
    doc.add_heading("DOO U Report", level=1)
    doc.add_paragraph(f"Organisation: {report_data.get('organisation_profile', {}).get('name', 'Unknown')}")
    doc.add_paragraph(f"Overall score: {report_data.get('overall_score', 'n/a')}")
    doc.add_paragraph("This placeholder report preserves the template and marks the current limitation of automated section injection.")
    doc.save(path)
    return True


def _slugify(value: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in value)
    slug = "-".join(part for part in slug.split("-") if part)
    return slug or "organisation"


def _write_batch_index(target_root: Path, generated: list[dict[str, Any]]) -> None:
    df = pd.DataFrame(generated)
    df.to_csv(target_root / "batch_index.csv", index=False)
    df.to_excel(target_root / "batch_index.xlsx", index=False)


def _write_batch_quality_report(target_root: Path, generated: list[dict[str, Any]]) -> None:
    rows = []
    for item in generated:
        rows.append(
            {
                "organisation": item["organisation_name"],
                "report_data": item["report_data_path"],
                "docx": item["docx_path"],
                "pdf": item["pdf_path"] or "MISSING",
            }
        )
    html = "<html><body><h1>Batch Quality Report</h1><ul>"
    for row in rows:
        html += f"<li>{row['organisation']}: PDF={row['pdf']}</li>"
    html += "</ul></body></html>"
    (target_root / "batch_quality_report.html").write_text(html, encoding="utf-8")
