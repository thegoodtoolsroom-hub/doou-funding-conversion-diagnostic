from pathlib import Path

from engine.limesurvey_decoder import decode_limesurvey_response_file
from engine.scoring_engine import score_decoded_responses


ROOT = Path("test_data/BATCH_04_TEST_DATA_UPLOAD_FOURTH")
BATCH_CSV = ROOT / "DOO_U_5_Dummy_Pilot_Client_Test_Responses_BATCH_LimeSurvey_Code_Style.csv"
BATCH_XLSX = ROOT / "DOO_U_5_Dummy_Pilot_Client_Test_Responses_BATCH_LimeSurvey_Code_Style.xlsx"


def test_scoring_runs_on_batch_csv():
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)

    assert len(scored) == 5
    for item in scored:
        assert item.decoded_scored_signals > 0
        assert len(item.driver_scores) == 24
        assert len(item.variable_scores) == 12
        assert 0 <= item.overall_readiness_score <= 100
        assert item.top_repair_priorities
        assert item.top_strengths


def test_scoring_runs_on_batch_xlsx():
    decoded = decode_limesurvey_response_file(BATCH_XLSX)
    scored = score_decoded_responses(decoded)

    assert len(scored) == 5
    for item in scored:
        assert item.decoded_scored_signals > 0
        assert item.overall_readiness_score >= 0
        assert item.overall_readiness_score <= 100


def test_scored_organisations_have_distinct_patterns():
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)

    assert len({round(item.overall_readiness_score, 2) for item in scored}) >= 3
    assert not all(item.overall_readiness_score == 50.0 for item in scored)


def test_variable_weights_total_100_percent():
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)

    total = round(sum(next(iter(scored)).variable_weights.values()), 2)
    assert total == 100.0


def test_no_org_gets_all_default_50_percent_variables():
    decoded = decode_limesurvey_response_file(BATCH_CSV)
    scored = score_decoded_responses(decoded)

    assert not any(all(value == 50.0 for value in item.variable_scores.values()) for item in scored)
