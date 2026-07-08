from __future__ import annotations

import json
from pathlib import Path

from engine.generate_sample import main as generate_sample
from engine.limesurvey_decoder import decode_limesurvey_response_file
from engine.report_content_builder import build_report_content, ReportContentBuilderError
from engine.report_data_builder import build_report_data_bundle
from engine.scoring_engine import score_decoded_responses


ROOT = Path("test_data/BATCH_04_TEST_DATA_UPLOAD_FOURTH")
BATCH_CSV = ROOT / "DOO_U_5_Dummy_Pilot_Client_Test_Responses_BATCH_LimeSurvey_Code_Style.csv"


def test_build_report_content_from_sample_data():
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)
    report_bundle = build_report_data_bundle(decoded, scored)

    assert len(report_bundle) == 5
    for report_data in report_bundle:
        content = build_report_content(report_data)
        
        assert content["organisation_name"]
        assert content["overall_score"] > 0
        assert content["result_band"]
        assert "variable_scores" in content
        assert len(content["variable_scores"]) == 12
        assert "assessment_area_scores" in content
        assert len(content["assessment_area_scores"]) == 24
        assert "journey_stage_scores" in content
        assert len(content["journey_stage_scores"]) == 5
        assert "diagnostic_confidence_score" in content
        assert 0 <= content["diagnostic_confidence_score"] <= 100


def test_build_report_content_all_organisations_have_different_scores():
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)
    report_bundle = build_report_data_bundle(decoded, scored)

    overall_scores = set()
    for report_data in report_bundle:
        content = build_report_content(report_data)
        overall_scores.add(content["overall_score"])
    
    # All five organisations should have different overall scores
    assert len(overall_scores) == 5, f"Expected 5 unique scores, got {len(overall_scores)}"


def test_build_report_content_with_zero_signals_raises_error():
    report_data = {
        "organisation_profile": {"name": "Test Org"},
        "decoded_scored_signal_count": 0,
        "overall_score": 50,
        "result_band": "Test",
        "variable_scores": {},
    }
    
    try:
        build_report_content(report_data)
        assert False, "Should have raised ReportContentBuilderError"
    except ReportContentBuilderError as e:
        assert "no decoded scored signals" in str(e)


def test_build_report_content_variable_scores_labeled():
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)
    report_bundle = build_report_data_bundle(decoded, scored)

    report_data = report_bundle[0]
    content = build_report_content(report_data)
    
    variable_scores = content["variable_scores"]
    assert len(variable_scores) == 12
    
    for var_score in variable_scores:
        assert "code" in var_score
        assert "label" in var_score
        assert "score" in var_score
        assert var_score["code"].startswith("R")
        assert isinstance(var_score["score"], float)


def test_build_report_content_assessment_area_scores_labeled():
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)
    report_bundle = build_report_data_bundle(decoded, scored)

    report_data = report_bundle[0]
    content = build_report_content(report_data)
    
    assessment_scores = content["assessment_area_scores"]
    assert len(assessment_scores) == 24
    
    for area_score in assessment_scores:
        assert "code" in area_score
        assert "label" in area_score
        assert "score" in area_score
        assert area_score["code"].startswith("D")
        assert isinstance(area_score["score"], float)


def test_build_report_content_journey_stage_scores_labeled():
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)
    report_bundle = build_report_data_bundle(decoded, scored)

    report_data = report_bundle[0]
    content = build_report_content(report_data)
    
    journey_scores = content["journey_stage_scores"]
    assert len(journey_scores) == 5
    
    for stage_score in journey_scores:
        assert "stage" in stage_score
        assert "label" in stage_score
        assert "score" in stage_score
        assert stage_score["stage"].startswith("stage_")
        assert isinstance(stage_score["score"], float)


def test_build_report_content_preserves_protection_flags():
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)
    report_bundle = build_report_data_bundle(decoded, scored)

    for report_data in report_bundle:
        content = build_report_content(report_data)
        
        # Check that flags are preserved
        assert isinstance(content["protected_evidence_flag"], bool)
        assert isinstance(content["unsafe_route_flag"], bool)
        assert isinstance(content["manual_review_flags"], list)
        assert isinstance(content["manual_review_required"], bool)


def test_diagnostic_confidence_score_increases_with_signals():
    """Test that diagnostic confidence increases with more decoded signals."""
    report_data_low = {
        "organisation_profile": {"name": "Low Signal Org"},
        "decoded_scored_signal_count": 50,
        "overall_score": 50,
        "result_band": "Test",
        "variable_scores": {"R01": 50, "R02": 50, "R03": 50, "R04": 50, "R05": 50, "R06": 50, "R07": 50, "R08": 50, "R09": 50, "R10": 50, "R11": 50, "R12": 50},
    }
    
    report_data_high = {
        "organisation_profile": {"name": "High Signal Org"},
        "decoded_scored_signal_count": 250,
        "overall_score": 50,
        "result_band": "Test",
        "variable_scores": {"R01": 80, "R02": 20, "R03": 75, "R04": 30, "R05": 85, "R06": 25, "R07": 75, "R08": 30, "R09": 80, "R10": 20, "R11": 70, "R12": 35},
    }
    
    content_low = build_report_content(report_data_low)
    content_high = build_report_content(report_data_high)
    
    # High signal count with good spread should have higher confidence
    assert content_high["diagnostic_confidence_score"] > content_low["diagnostic_confidence_score"]
