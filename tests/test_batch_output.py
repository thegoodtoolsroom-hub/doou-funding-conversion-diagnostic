from pathlib import Path

from engine.generate_sample import main as generate_sample
from engine.limesurvey_decoder import decode_limesurvey_response_file
from engine.scoring_engine import score_decoded_responses
from engine.report_data_builder import build_report_data_bundle
from engine.batch_output import generate_batch_outputs


ROOT = Path("test_data/BATCH_04_TEST_DATA_UPLOAD_FOURTH")
BATCH_CSV = ROOT / "DOO_U_5_Dummy_Pilot_Client_Test_Responses_BATCH_LimeSurvey_Code_Style.csv"


def test_generate_batch_outputs_creates_expected_artifacts(tmp_path):
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)
    report_bundle = build_report_data_bundle(decoded, scored)

    output_root = tmp_path / "outputs"
    generated = generate_batch_outputs(decoded, scored, report_bundle, output_root)

    assert len(generated) == 5
    assert (output_root / "batch_index.csv").exists()
    assert (output_root / "batch_index.xlsx").exists()
    assert (output_root / "batch_quality_report.html").exists()

    for item in generated:
        org_dir = output_root / item["organisation_slug"]
        assert org_dir.exists()
        assert (org_dir / "report_data.json").exists()
        assert (org_dir / "response_audit.json").exists()
        assert (org_dir / "report.docx").exists()
        assert (org_dir / "report.html").exists(), f"HTML report missing for {item['organisation_name']}"


def test_generate_batch_outputs_html_reports_generated(tmp_path):
    """Test that HTML reports are generated for all organisations."""
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)
    report_bundle = build_report_data_bundle(decoded, scored)

    output_root = tmp_path / "outputs"
    generated = generate_batch_outputs(decoded, scored, report_bundle, output_root)

    assert len(generated) == 5
    
    for item in generated:
        assert "html_path" in item
        assert "html_status" in item
        assert item["html_status"] in ["HTML_RENDERED", "HTML_RENDER_ERROR"]
        
        if item["html_status"] == "HTML_RENDERED":
            html_path = Path(item["html_path"])
            assert html_path.exists()


def test_generate_batch_outputs_pdf_status_tracked(tmp_path):
    """Test that PDF rendering status is tracked."""
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)
    report_bundle = build_report_data_bundle(decoded, scored)

    output_root = tmp_path / "outputs"
    generated = generate_batch_outputs(decoded, scored, report_bundle, output_root)

    assert len(generated) == 5
    
    for item in generated:
        assert "pdf_status" in item
        assert item["pdf_status"] in ["PDF_RENDERED", "PDF_RENDER_ERROR", "PDF_RENDER_NOT_ATTEMPTED"]


def test_generate_sample_writes_persistent_outputs(tmp_path):
    output_root = tmp_path / "outputs" / "sample_batch"
    generate_sample(output_root)

    assert (output_root / "batch_index.csv").exists()
    assert (output_root / "batch_quality_report.html").exists()
    assert (output_root / "batch_index.xlsx").exists()
    assert len(list(output_root.glob("*"))) >= 1


def test_batch_outputs_html_files_contain_organisation_names(tmp_path):
    """Test that HTML reports contain organisation names."""
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)
    report_bundle = build_report_data_bundle(decoded, scored)

    output_root = tmp_path / "outputs"
    generated = generate_batch_outputs(decoded, scored, report_bundle, output_root)

    for item in generated:
        if item["html_status"] == "HTML_RENDERED":
            html_path = Path(item["html_path"])
            html_content = html_path.read_text(encoding="utf-8")
            assert item["organisation_name"] in html_content


def test_batch_outputs_all_organisations_have_unique_html_reports(tmp_path):
    """Test that all five sample organisations have different HTML content."""
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)
    report_bundle = build_report_data_bundle(decoded, scored)

    output_root = tmp_path / "outputs"
    generated = generate_batch_outputs(decoded, scored, report_bundle, output_root)

    html_contents = set()
    for item in generated:
        if item["html_status"] == "HTML_RENDERED":
            html_path = Path(item["html_path"])
            content = html_path.read_text(encoding="utf-8")
            # Use a hash to check uniqueness (content would be too large)
            html_contents.add(hash(content))
    
    # All should be unique
    assert len(html_contents) == 5

