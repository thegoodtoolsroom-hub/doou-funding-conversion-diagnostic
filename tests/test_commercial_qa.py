import json
from pathlib import Path

from docx import Document

from engine.commercial_qa import inspect_batch_output, render_batch_quality_report


def _write_org(batch_root: Path, name: str, *, decoded_signal_count: int = 10, variable_scores: dict[str, float] | None = None, manual_review_flags: list[str] | None = None, docx_text: str | None = None, pdf_present: bool = True, font_error: bool = False) -> None:
    org_dir = batch_root / name
    org_dir.mkdir(parents=True, exist_ok=True)
    report_data = {
        "organisation_profile": {"name": name},
        "overall_score": 72.0,
        "decoded_scored_signal_count": decoded_signal_count,
        "variable_scores": variable_scores or {"var_1": 50.0, "var_2": 60.0, "var_3": 70.0, "var_4": 80.0, "var_5": 90.0, "var_6": 100.0, "var_7": 50.0, "var_8": 40.0, "var_9": 30.0, "var_10": 20.0, "var_11": 10.0, "var_12": 0.0},
        "manual_review_flags": manual_review_flags or [],
    }
    (org_dir / "report_data.json").write_text(json.dumps(report_data), encoding="utf-8")

    doc = Document()
    doc.add_paragraph(docx_text or "Safe section content")
    doc.save(org_dir / "report.docx")

    if pdf_present:
        (org_dir / "report.pdf").write_bytes(b"%PDF-1.4")
    if font_error:
        (org_dir / "FONT_QA_ERROR.txt").write_text("FONT_QA_ERROR", encoding="utf-8")


def test_inspects_existing_docx_and_pdf_and_flags_placeholder_content(tmp_path):
    batch_root = tmp_path / "outputs" / "sample_batch"
    _write_org(batch_root, "org-a", docx_text="This placeholder report preserves the template and marks the current limitation of automated section injection.")

    results = inspect_batch_output(batch_root)

    assert len(results) == 1
    assert results[0]["structurally_generated"] is True
    assert results[0]["docx_present"] is True
    assert results[0]["pdf_present"] is True
    assert results[0]["template_quality_blocked"] is True
    assert results[0]["placeholder_generic_content_blocked"] is True
    assert results[0]["font_qa_blocked"] is True
    assert results[0]["commercial_quality_status"] == "BLOCKED"
    assert "not yet final commercial quality" in results[0]["status_message"]


def test_checks_five_organisations_and_content_safety_conditions(tmp_path):
    batch_root = tmp_path / "outputs" / "sample_batch"
    _write_org(batch_root, "org-1", decoded_signal_count=20, variable_scores={f"var_{i}": 50.0 for i in range(1, 13)}, manual_review_flags=[])
    _write_org(batch_root, "org-2", decoded_signal_count=32, variable_scores={f"var_{i}": 50.0 for i in range(1, 13)}, manual_review_flags=["unsafe route requires manual review"])
    _write_org(batch_root, "org-3", decoded_signal_count=41, variable_scores={f"var_{i}": 50.0 for i in range(1, 13)}, manual_review_flags=["protected evidence requires review"])
    _write_org(batch_root, "org-4", decoded_signal_count=16, variable_scores={f"var_{i}": 55.0 if i % 2 == 0 else 50.0 for i in range(1, 13)}, manual_review_flags=[])
    _write_org(batch_root, "org-5", decoded_signal_count=27, variable_scores={f"var_{i}": 50.0 for i in range(1, 13)}, manual_review_flags=["unsafe route requires manual review", "protected evidence requires review"])

    results = inspect_batch_output(batch_root)
    html = render_batch_quality_report(batch_root, results)

    assert len(results) == 5
    assert all(item["decoded_scored_signal_count"] > 0 for item in results)
    assert any(item["scores_not_all_fifty"] for item in results)
    assert any(item["manual_review_required"] for item in results)
    assert "commercial quality report" in html.lower()
    assert all(item["commercial_quality_status"] in {"PASS", "WARNING", "BLOCKED"} for item in results)


def test_marks_font_qa_blocked_when_font_verification_is_missing(tmp_path):
    batch_root = tmp_path / "outputs" / "sample_batch"
    _write_org(batch_root, "org-font", docx_text="Safe section content", pdf_present=True, font_error=False)

    results = inspect_batch_output(batch_root)

    assert results[0]["font_qa_blocked"] is True
    assert results[0]["font_qa_status"] == "FONT_QA_BLOCKED"
    assert results[0]["commercial_quality_status"] == "BLOCKED"
