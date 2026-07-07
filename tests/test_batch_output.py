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
        assert (org_dir / "report.pdf").exists() or (org_dir / "FONT_QA_ERROR.txt").exists()


def test_generate_sample_writes_persistent_outputs(tmp_path):
    output_root = tmp_path / "outputs" / "sample_batch"
    generate_sample(output_root)

    assert (output_root / "batch_index.csv").exists()
    assert (output_root / "batch_quality_report.html").exists()
    assert (output_root / "batch_index.xlsx").exists()
    assert len(list(output_root.glob("*"))) >= 1
