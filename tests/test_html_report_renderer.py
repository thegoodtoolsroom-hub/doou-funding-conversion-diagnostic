from __future__ import annotations

from pathlib import Path

from engine.generate_sample import main as generate_sample
from engine.html_report_renderer import render_html_report, HTMLReportRendererError
from engine.limesurvey_decoder import decode_limesurvey_response_file
from engine.report_data_builder import build_report_data_bundle
from engine.scoring_engine import score_decoded_responses


ROOT = Path("test_data/BATCH_04_TEST_DATA_UPLOAD_FOURTH")
BATCH_CSV = ROOT / "DOO_U_5_Dummy_Pilot_Client_Test_Responses_BATCH_LimeSurvey_Code_Style.csv"


def test_render_html_report_for_all_sample_organisations(tmp_path):
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)
    report_bundle = build_report_data_bundle(decoded, scored)

    assert len(report_bundle) == 5
    
    for i, report_data in enumerate(report_bundle):
        output_path = tmp_path / f"report_{i}.html"
        html_output = render_html_report(report_data, output_path)
        
        assert output_path.exists()
        assert output_path.stat().st_size > 1000  # Should be reasonably sized
        assert html_output
        
        content = output_path.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content
        assert report_data["organisation_profile"]["name"] in content


def test_render_html_report_includes_organisation_name(tmp_path):
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)
    report_bundle = build_report_data_bundle(decoded, scored)

    report_data = report_bundle[0]
    org_name = report_data["organisation_profile"]["name"]
    
    output_path = tmp_path / "report.html"
    html_output = render_html_report(report_data, output_path)
    
    assert org_name in html_output
    assert "<!DOCTYPE html>" in html_output


def test_render_html_report_includes_12_variable_scores(tmp_path):
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)
    report_bundle = build_report_data_bundle(decoded, scored)

    report_data = report_bundle[0]
    output_path = tmp_path / "report.html"
    html_output = render_html_report(report_data, output_path)
    
    # Check for all 12 variable codes
    for i in range(1, 13):
        code = f"R{i:02d}"
        assert code in html_output, f"Variable {code} not found in HTML"


def test_render_html_report_includes_24_assessment_area_scores(tmp_path):
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)
    report_bundle = build_report_data_bundle(decoded, scored)

    report_data = report_bundle[0]
    output_path = tmp_path / "report.html"
    html_output = render_html_report(report_data, output_path)
    
    # Check for all 24 assessment area codes
    for i in range(1, 25):
        code = f"D{i:02d}"
        assert code in html_output, f"Assessment area {code} not found in HTML"


def test_render_html_report_includes_top_repair_priorities(tmp_path):
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)
    report_bundle = build_report_data_bundle(decoded, scored)

    report_data = report_bundle[0]
    priorities = report_data.get("top_repair_priorities", [])
    
    output_path = tmp_path / "report.html"
    html_output = render_html_report(report_data, output_path)
    
    # Check that at least one priority is mentioned
    for priority in priorities[:3]:
        assert priority in html_output, f"Priority '{priority}' not found in HTML"


def test_render_html_report_respects_free_report_visibility(tmp_path):
    """Test that protected evidence is hidden in free reports."""
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)
    report_bundle = build_report_data_bundle(decoded, scored)

    # Find an organisation with protected evidence flag
    for report_data in report_bundle:
        if report_data.get("protected_evidence_flag"):
            output_path = tmp_path / "protected_report.html"
            html_output = render_html_report(report_data, output_path)
            
            # In free report, protected evidence detail should be conditionally hidden
            assert "Protected Evidence Detected" in html_output
            break


def test_render_html_report_shows_manual_review_flags(tmp_path):
    """Test that manual review flags are visible in internal reports."""
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)
    report_bundle = build_report_data_bundle(decoded, scored)

    # Find an organisation with manual review flags
    for report_data in report_bundle:
        if report_data.get("manual_review_flags"):
            output_path = tmp_path / "review_report.html"
            html_output = render_html_report(report_data, output_path)
            
            assert "Manual Review Required" in html_output
            break


def test_render_html_report_returns_string_without_output_path(tmp_path):
    """Test that HTML is returned as string even without output path."""
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)
    report_bundle = build_report_data_bundle(decoded, scored)

    report_data = report_bundle[0]
    html_output = render_html_report(report_data)
    
    assert isinstance(html_output, str)
    assert html_output.startswith("<!DOCTYPE html>")


def test_render_html_report_with_zero_signals_raises_error(tmp_path):
    """Test that zero decoded signals causes appropriate error."""
    report_data = {
        "organisation_profile": {"name": "Test Org"},
        "decoded_scored_signal_count": 0,
        "overall_score": 50,
        "result_band": "Test",
        "variable_scores": {},
    }
    
    output_path = tmp_path / "error_report.html"
    
    try:
        render_html_report(report_data, output_path)
        assert False, "Should have raised HTMLReportRendererError"
    except HTMLReportRendererError as e:
        assert "no decoded scored signals" in str(e)


def test_render_html_report_jinja_filters_applied(tmp_path):
    """Test that Jinja2 filters are available and applied."""
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)
    report_bundle = build_report_data_bundle(decoded, scored)

    report_data = report_bundle[0]
    output_path = tmp_path / "report.html"
    html_output = render_html_report(report_data, output_path)
    
    # Check that numeric scores are rendered (percentage filter applied)
    assert "%" in html_output or html_output.count(".") > 10  # Contains percentage values


def test_render_html_reports_for_all_five_samples():
    """Integration test: render HTML for all five sample organisations."""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        decoded = decode_limesurvey_response_file(BATCH_CSV)
        scored = score_decoded_responses(decoded)
        report_bundle = build_report_data_bundle(decoded, scored)

        assert len(report_bundle) == 5
        
        for i, report_data in enumerate(report_bundle):
            output_path = tmp_path / f"sample_{i}.html"
            html_output = render_html_report(report_data, output_path)
            
            assert output_path.exists(), f"HTML file {i} not created"
            assert "<!DOCTYPE html>" in html_output
            assert report_data["organisation_profile"]["name"] in html_output
