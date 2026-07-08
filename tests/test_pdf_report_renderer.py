from __future__ import annotations

from pathlib import Path

from engine.html_report_renderer import render_html_report
from engine.limesurvey_decoder import decode_limesurvey_response_file
from engine.pdf_report_renderer import render_pdf_report, is_pdf_rendering_available
from engine.report_data_builder import build_report_data_bundle
from engine.scoring_engine import score_decoded_responses


ROOT = Path("test_data/BATCH_04_TEST_DATA_UPLOAD_FOURTH")
BATCH_CSV = ROOT / "DOO_U_5_Dummy_Pilot_Client_Test_Responses_BATCH_LimeSurvey_Code_Style.csv"


def test_pdf_rendering_status():
    """Test that PDF rendering availability is properly detected."""
    status = is_pdf_rendering_available()
    assert isinstance(status, bool)


def test_render_pdf_report_or_returns_render_error(tmp_path):
    """Test that PDF rendering returns proper status (rendered or error)."""
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)
    report_bundle = build_report_data_bundle(decoded, scored)

    report_data = report_bundle[0]
    html_content = render_html_report(report_data)
    
    pdf_path = tmp_path / "report.pdf"
    result = render_pdf_report(html_content, pdf_path)
    
    # Should return either success or clear error status
    assert "status" in result
    assert result["status"] in ["PDF_RENDERED", "PDF_RENDER_ERROR", "PDF_RENDER_NOT_ATTEMPTED"]


def test_render_pdf_report_for_all_five_samples():
    """Test that PDF rendering is attempted for all five sample organisations."""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        decoded = decode_limesurvey_response_file(BATCH_CSV)
        scored = score_decoded_responses(decoded)
        report_bundle = build_report_data_bundle(decoded, scored)

        assert len(report_bundle) == 5
        
        pdf_results = []
        for i, report_data in enumerate(report_bundle):
            html_content = render_html_report(report_data)
            pdf_path = tmp_path / f"sample_{i}.pdf"
            result = render_pdf_report(html_content, pdf_path)
            
            assert "status" in result
            assert result["status"] in ["PDF_RENDERED", "PDF_RENDER_ERROR", "PDF_RENDER_NOT_ATTEMPTED"]
            pdf_results.append(result["status"])
        
        # At least some attempt should have been made
        assert len(pdf_results) == 5


def test_render_pdf_report_returns_explicit_status_on_error():
    """Test that PDF rendering errors are explicit and documented."""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Simple HTML to render
        html_content = "<html><body><h1>Test</h1></body></html>"
        pdf_path = tmp_path / "test.pdf"
        
        result = render_pdf_report(html_content, pdf_path)
        
        # Result should clearly indicate status
        assert "status" in result
        assert "message" in result
        assert result["status"] in ["PDF_RENDERED", "PDF_RENDER_ERROR", "PDF_RENDER_NOT_ATTEMPTED"]


def test_pdf_render_graceful_fallback_when_weasyprint_unavailable():
    """
    Test that PDF rendering gracefully handles missing weasyprint.
    
    If weasyprint is not available, the status should be PDF_RENDER_ERROR
    with a clear message, not a hard failure.
    """
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        html_content = "<html><body><p>Test content</p></body></html>"
        pdf_path = tmp_path / "test.pdf"
        
        result = render_pdf_report(html_content, pdf_path)
        
        # Should return a clear status dict, never raise an exception
        assert isinstance(result, dict)
        assert "status" in result
        assert "message" in result
        
        # If weasyprint is unavailable, should be explicit
        if not is_pdf_rendering_available():
            assert result["status"] == "PDF_RENDER_ERROR"
            assert "weasyprint" in result["message"].lower() or "unavailable" in result["message"].lower()


def test_pdf_render_result_structure():
    """Test that PDF render result has expected structure."""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        html_content = "<html><body><h1>Test Report</h1></body></html>"
        pdf_path = tmp_path / "test.pdf"
        
        result = render_pdf_report(html_content, pdf_path)
        
        # Result should have these keys
        assert "status" in result
        assert "message" in result
        assert "html_rendered" in result
        assert "pdf_path" in result
        
        # html_rendered should be True (we passed valid HTML)
        assert result["html_rendered"] is True


def test_pdf_render_creates_directory_if_needed(tmp_path):
    """Test that PDF renderer creates output directory if it doesn't exist."""
    html_content = "<html><body><p>Test</p></body></html>"
    
    # Use a nested path that doesn't exist
    pdf_path = tmp_path / "nested" / "dir" / "report.pdf"
    
    result = render_pdf_report(html_content, pdf_path)
    
    # Should have attempted to render (not raise exception about missing directory)
    assert isinstance(result, dict)
    assert "status" in result
    
    # Directory should be created
    assert pdf_path.parent.exists()


def test_pdf_and_html_generation_workflow(tmp_path):
    """Integration test: HTML → PDF workflow for sample organisation."""
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)
    report_bundle = build_report_data_bundle(decoded, scored)

    report_data = report_bundle[0]
    
    # Step 1: Generate HTML
    html_path = tmp_path / "report.html"
    html_output = render_html_report(report_data, html_path)
    assert html_path.exists()
    
    # Step 2: Generate PDF from HTML
    pdf_path = tmp_path / "report.pdf"
    html_content = html_path.read_text(encoding="utf-8")
    pdf_result = render_pdf_report(html_content, pdf_path)
    
    # Step 3: Verify workflow completed
    assert pdf_result["status"] in ["PDF_RENDERED", "PDF_RENDER_ERROR", "PDF_RENDER_NOT_ATTEMPTED"]
    assert pdf_result["html_rendered"] is True
    
    # If PDF was successfully rendered, file should exist
    if pdf_result["status"] == "PDF_RENDERED":
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 0
