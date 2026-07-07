from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import re

import pandas as pd


class LimeSurveyDecoderError(Exception):
    """Raised when a LimeSurvey response file cannot be decoded safely."""


@dataclass(frozen=True)
class DecodedResponse:
    organisation_name: str
    decoded_scored_signals: int
    unknown_fields: list[str]
    missing_required_fields: list[str]
    raw_rows: list[dict[str, Any]]


class LimeSurveyDecoder:
    def __init__(self) -> None:
        self.required_fields = {"SETUP_ORG_NAME"}

    def decode_file(self, path: str | Path) -> list[DecodedResponse]:
        source = Path(path)
        if not source.exists():
            raise LimeSurveyDecoderError(f"Response file not found: {source}")

        if source.suffix.lower() == ".csv":
            df = pd.read_csv(source)
        elif source.suffix.lower() in {".xlsx", ".xls"}:
            df = pd.read_excel(source)
        else:
            raise LimeSurveyDecoderError(f"Unsupported file type: {source}")

        if df.empty:
            raise LimeSurveyDecoderError(f"Response file is empty: {source}")

        return self.decode_dataframe(df)

    def decode_dataframe(self, df: pd.DataFrame) -> list[DecodedResponse]:
        rows: list[DecodedResponse] = []
        for _, row in df.iterrows():
            organisation_name = self._organisation_name(row)
            if not organisation_name:
                continue

            decoded_codes = self._decode_row(row)
            unknown_fields = self._unknown_fields(row)
            missing_required_fields = self._missing_required_fields(row)
            signal_count = len(decoded_codes)

            if signal_count == 0:
                raise LimeSurveyDecoderError(
                    f"Decoded scored signals = 0 for organisation '{organisation_name}'. "
                    "Cannot generate a report."
                )

            rows.append(
                DecodedResponse(
                    organisation_name=organisation_name,
                    decoded_scored_signals=signal_count,
                    unknown_fields=unknown_fields,
                    missing_required_fields=missing_required_fields,
                    raw_rows=[row.to_dict()],
                )
            )

        if not rows:
            raise LimeSurveyDecoderError("No organisation rows detected in response file.")
        return rows

    def _organisation_name(self, row: pd.Series) -> str:
        for column in row.index:
            if str(column).strip().upper() == "SETUP_ORG_NAME":
                value = row[column]
                if pd.notna(value):
                    value = str(value).strip()
                    if value:
                        return value
        return ""

    def _decode_row(self, row: pd.Series) -> set[str]:
        decoded: set[str] = set()
        for column in row.index:
            if not isinstance(column, str):
                continue
            key = column.strip().upper()
            if not re.match(r"^[A-Z0-9_]+$", key):
                continue
            if not self._looks_like_response_column(key):
                continue
            value = row[column]
            if pd.isna(value):
                continue
            text = str(value).strip()
            if not text:
                continue
            if self._looks_like_single_choice(text):
                decoded.add(key)
                continue
            if self._looks_like_matrix_indicator(text):
                decoded.add(key)
                continue
            if self._looks_like_multi_select(text):
                decoded.add(key)
                continue
        return decoded

    def _unknown_fields(self, row: pd.Series) -> list[str]:
        unknown = []
        for column in row.index:
            if not isinstance(column, str):
                continue
            key = str(column).strip().upper()
            if key in self.required_fields:
                continue
            if self._is_metadata_field(key):
                continue
            if not self._looks_like_response_column(key):
                continue
            if pd.isna(row[column]):
                continue
            if str(row[column]).strip() and not self._looks_like_decodable_answer(row[column]):
                unknown.append(column)
        return unknown

    def _missing_required_fields(self, row: pd.Series) -> list[str]:
        missing = []
        for field in sorted(self.required_fields):
            if pd.isna(row.get(field, pd.NA)):
                missing.append(field)
        return missing

    def _looks_like_single_choice(self, text: str) -> bool:
        return re.fullmatch(r"A\d{2,3}", text) is not None

    def _looks_like_matrix_indicator(self, text: str) -> bool:
        return re.fullmatch(r"(?:D\d+:A\d{2,3})(?:;D\d+:A\d{2,3})*", text) is not None

    def _looks_like_multi_select(self, text: str) -> bool:
        return ";" in text or text.startswith("SQ") or text.startswith("PQC") or text == "Y"

    def _looks_like_response_column(self, key: str) -> bool:
        if key == "SETUP_ORG_NAME":
            return True
        return key.startswith("R")

    def _looks_like_decodable_answer(self, value: Any) -> bool:
        if pd.isna(value):
            return False
        text = str(value).strip()
        if not text:
            return False
        return (
            self._looks_like_single_choice(text)
            or self._looks_like_matrix_indicator(text)
            or self._looks_like_multi_select(text)
        )

    def _is_metadata_field(self, key: str) -> bool:
        return key.startswith(("RESPONSE_", "SYNTHETIC_", "SOURCE_", "TEST_", "EXPECTED_", "SETUP_"))


def decode_limesurvey_response_file(path: str | Path) -> list[DecodedResponse]:
    return LimeSurveyDecoder().decode_file(path)
