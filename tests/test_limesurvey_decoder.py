from pathlib import Path

import pandas as pd
import pytest

from engine.limesurvey_decoder import LimeSurveyDecoderError, decode_limesurvey_response_file


ROOT = Path("test_data/BATCH_04_TEST_DATA_UPLOAD_FOURTH")
BATCH_FILE = ROOT / "DOO_U_5_Dummy_Pilot_Client_Test_Responses_BATCH_LimeSurvey_Code_Style.csv"
SINGLE_RESPONSE_FILES = sorted(ROOT.glob("TEST_RESPONSE_*.csv"))


def test_batch_file_decodes_all_dummy_responses():
    responses = decode_limesurvey_response_file(BATCH_FILE)

    assert len(responses) == 5
    for response in responses:
        assert response.organisation_name
        assert response.decoded_scored_signals > 0
        assert response.unknown_fields == []
        assert response.missing_required_fields == []


@pytest.mark.parametrize("path", SINGLE_RESPONSE_FILES)
def test_single_response_files_decode_signals(path):
    responses = decode_limesurvey_response_file(path)

    assert len(responses) == 1
    response = responses[0]
    assert response.organisation_name
    assert response.decoded_scored_signals > 0
    assert response.unknown_fields == []
    assert response.missing_required_fields == []


def test_zero_signal_response_raises_clear_error(tmp_path):
    path = tmp_path / "empty_response.csv"
    pd.DataFrame({"SETUP_ORG_NAME": ["Example Org"], "R01_D02_Q01": [""]}).to_csv(path, index=False)

    with pytest.raises(LimeSurveyDecoderError, match="Decoded scored signals"):
        decode_limesurvey_response_file(path)
