from __future__ import annotations

from pathlib import Path

from engine.batch_output import generate_batch_outputs
from engine.limesurvey_decoder import decode_limesurvey_response_file
from engine.report_data_builder import build_report_data_bundle
from engine.scoring_engine import score_decoded_responses


def main(output_root: str | Path | None = None) -> None:
    root = Path(__file__).resolve().parent.parent
    data_dir = root / "test_data" / "BATCH_04_TEST_DATA_UPLOAD_FOURTH"
    batch_path = data_dir / "DOO_U_5_Dummy_Pilot_Client_Test_Responses_BATCH_LimeSurvey_Code_Style.csv"
    target_root = Path(output_root) if output_root is not None else root / "outputs" / "sample_batch"

    if not batch_path.exists():
        raise FileNotFoundError(f"Batch response file not found: {batch_path}")

    decoded = decode_limesurvey_response_file(batch_path)
    scored = score_decoded_responses(decoded)
    report_bundle = build_report_data_bundle(decoded, scored)
    generate_batch_outputs(decoded, scored, report_bundle, target_root)


if __name__ == "__main__":
    main()
