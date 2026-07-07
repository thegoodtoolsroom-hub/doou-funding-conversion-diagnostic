from pathlib import Path

from engine.limesurvey_decoder import decode_limesurvey_response_file
from engine.scoring_engine import score_decoded_responses
from engine.report_data_builder import build_report_data_bundle, write_report_data_bundle


ROOT = Path("test_data/BATCH_04_TEST_DATA_UPLOAD_FOURTH")
BATCH_CSV = ROOT / "DOO_U_5_Dummy_Pilot_Client_Test_Responses_BATCH_LimeSurvey_Code_Style.csv"


def test_report_data_bundle_contains_required_sections(tmp_path):
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)

    bundle = build_report_data_bundle(decoded, scored)

    assert len(bundle) == 5
    for item in bundle:
        assert "organisation_profile" in item
        assert "overall_score" in item
        assert "result_band" in item
        assert "variable_scores" in item
        assert "assessment_area_scores" in item
        assert "journey_stage_scores" in item
        assert "breakpoint_stage" in item
        assert "top_repair_priorities" in item
        assert "protected_evidence_flag" in item
        assert "unsafe_route_flag" in item
        assert "manual_review_flags" in item
        assert "free_report_visibility" in item
        assert "full_report_visibility" in item
        assert "decoded_scored_signal_count" in item


def test_protected_evidence_hides_free_report_details():
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)

    bundle = build_report_data_bundle(decoded, scored)
    sister = next(item for item in bundle if "Sister Ghana" in item["organisation_profile"]["name"])

    assert sister["protected_evidence_flag"] is True
    assert sister["free_report_visibility"]["protected_evidence_detail"] is False
    assert sister["full_report_visibility"]["protected_evidence_detail"] is True


def test_unsafe_routes_trigger_manual_review():
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)

    bundle = build_report_data_bundle(decoded, scored)
    treat = next(item for item in bundle if "TREAT" in item["organisation_profile"]["name"])

    assert treat["unsafe_route_flag"] is True
    assert any("unsafe route" in flag.lower() for flag in treat["manual_review_flags"])


def test_writes_report_data_json_files(tmp_path):
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)

    output_dir = tmp_path / "report_data"
    output_dir.mkdir(parents=True, exist_ok=True)
    written = write_report_data_bundle(decoded, scored, output_dir)

    assert len(written) == 5
    assert (output_dir / "report_data.json").exists()
