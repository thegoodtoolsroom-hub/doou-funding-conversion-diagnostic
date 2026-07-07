from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import re

from engine.limesurvey_decoder import DecodedResponse
from engine.product_lock_loader import MetricSignal, ProductLock, load_product_lock


@dataclass(frozen=True)
class ScoredOrganisation:
    organisation_name: str
    decoded_scored_signals: int
    driver_scores: dict[str, float]
    variable_scores: dict[str, float]
    variable_weights: dict[str, float]
    overall_readiness_score: float
    result_band: str
    top_strengths: list[str]
    top_repair_priorities: list[str]
    metric_scores: dict[str, float]


class ScoringEngine:
    def __init__(self, product_lock: ProductLock | None = None) -> None:
        self.product_lock = product_lock or load_product_lock(Path("product_lock"))
        self.variable_weights = {v.code: v.weight_percent for v in self.product_lock.variables}
        self.metrics_by_driver: dict[str, list[MetricSignal]] = self._group_metrics_by_driver()
        self.driver_to_variable = {d.code: d.variable_code for d in self.product_lock.assessment_areas}
        self.driver_names = {d.code: d.name for d in self.product_lock.assessment_areas}
        self.variable_names = {v.code: v.name for v in self.product_lock.variables}

    def score_response(self, response: DecodedResponse) -> ScoredOrganisation:
        if response.decoded_scored_signals <= 0:
            raise ValueError("Cannot score a response with zero decoded scored signals.")

        metric_scores = self._score_metrics(response)
        driver_scores = self._score_drivers(metric_scores)
        variable_scores = self._score_variables(driver_scores)
        overall_score = self._score_overall(variable_scores)
        band = self._band_for_score(overall_score)
        strengths = self._top_strengths(variable_scores)
        repairs = self._top_repairs(variable_scores)

        return ScoredOrganisation(
            organisation_name=response.organisation_name,
            decoded_scored_signals=response.decoded_scored_signals,
            driver_scores=driver_scores,
            variable_scores=variable_scores,
            variable_weights=self.variable_weights,
            overall_readiness_score=overall_score,
            result_band=band,
            top_strengths=strengths,
            top_repair_priorities=repairs,
            metric_scores=metric_scores,
        )

    def score_responses(self, responses: list[DecodedResponse]) -> list[ScoredOrganisation]:
        return [self.score_response(response) for response in responses]

    def _group_metrics_by_driver(self) -> dict[str, list[MetricSignal]]:
        grouped: dict[str, list[MetricSignal]] = {}
        for metric in self.product_lock.metrics:
            grouped.setdefault(metric.driver_code, []).append(metric)
        return grouped

    def _score_metrics(self, response: DecodedResponse) -> dict[str, float]:
        scores: dict[str, float] = {}
        for metric in self.product_lock.metrics:
            matching_values = [self._score_from_value(value) for value in self._matching_response_values(metric, response)]
            if matching_values:
                scores[metric.metric_id] = round(sum(matching_values) / len(matching_values), 2)
            else:
                scores[metric.metric_id] = 0.0
        return scores

    def _matching_response_values(self, metric: MetricSignal, response: DecodedResponse) -> list[Any]:
        values: list[Any] = []
        for row in response.raw_rows:
            for column, value in row.items():
                if not isinstance(column, str):
                    continue
                if str(column).strip().upper() == "SETUP_ORG_NAME":
                    continue
                key = str(column).strip().upper()
                if not self._is_response_cell(key):
                    continue
                if not self._is_responded_value(value):
                    continue
                if self._cell_matches_metric(key, metric):
                    values.append(value)
        return values

    def _cell_matches_metric(self, column: str, metric: MetricSignal) -> bool:
        key = column.strip().upper()
        if not key.startswith("R"):
            return False
        # Match by variable and driver from the LimeSurvey question code shape.
        parts = key.split("_")
        if len(parts) < 2:
            return False
        variable_code = parts[0]
        driver_code = None
        for part in parts[1:]:
            if part.startswith("D"):
                driver_code = part
                break
        if driver_code is None:
            return False
        return variable_code == metric.variable_code and driver_code == metric.driver_code

    def _is_response_cell(self, key: str) -> bool:
        return key.startswith("R")

    def _is_responded_value(self, value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, float) and value != value:
            return False
        text = str(value).strip()
        return bool(text)

    def _score_from_value(self, value: Any) -> float:
        text = str(value).strip()
        if not text:
            return 0.0

        if re.fullmatch(r"A\d{2,3}", text):
            option = int(text[1:])
            if option <= 1:
                return 20.0
            if option == 2:
                return 40.0
            if option == 3:
                return 60.0
            if option == 4:
                return 80.0
            return 100.0

        if re.fullmatch(r"(?:D\d+:A\d{2,3})(?:;D\d+:A\d{2,3})*", text):
            parts = text.split(";")
            scores = [self._score_from_value(part.split(":", 1)[1]) for part in parts if ":" in part]
            if scores:
                return round(sum(scores) / len(scores), 2)
            return 0.0

        if ";" in text:
            selections = [chunk for chunk in text.split(";") if chunk.strip()]
            if selections:
                return round(min(100.0, 100.0 * len(selections) / 6.0), 2)
            return 0.0

        if text == "Y":
            return 100.0

        return 0.0

    def _score_drivers(self, metric_scores: dict[str, float]) -> dict[str, float]:
        driver_scores: dict[str, float] = {}
        for driver_code in sorted({metric.driver_code for metric in self.product_lock.metrics}):
            metrics = self.metrics_by_driver.get(driver_code, [])
            if not metrics:
                continue
            values = [metric_scores.get(metric.metric_id, 0.0) for metric in metrics]
            driver_scores[driver_code] = round(sum(values) / max(len(values), 1), 2)
        return driver_scores

    def _score_variables(self, driver_scores: dict[str, float]) -> dict[str, float]:
        variable_scores: dict[str, float] = {}
        for variable in self.product_lock.variables:
            related_drivers = [d.code for d in self.product_lock.assessment_areas if d.variable_code == variable.code]
            values = [driver_scores.get(driver_code, 0.0) for driver_code in related_drivers]
            if not values:
                variable_scores[variable.code] = 0.0
            else:
                variable_scores[variable.code] = round(sum(values) / len(values), 2)
        return variable_scores

    def _score_overall(self, variable_scores: dict[str, float]) -> float:
        total_weighted = 0.0
        for variable_code, score in variable_scores.items():
            total_weighted += score * self.variable_weights[variable_code] / 100.0
        return round(total_weighted, 2)

    def _band_for_score(self, score: float) -> str:
        if score <= 20:
            return "Major Barrier / Locked"
        if score <= 40:
            return "Conversion Risk / Fragile"
        if score <= 60:
            return "Light Friction / Emerging"
        if score <= 80:
            return "Low Barrier / Functional"
        return "Strength / Strong"

    def _top_strengths(self, variable_scores: dict[str, float]) -> list[str]:
        ranked = sorted(variable_scores.items(), key=lambda item: item[1], reverse=True)[:3]
        return [self.variable_names.get(code, code) for code, _ in ranked]

    def _top_repairs(self, variable_scores: dict[str, float]) -> list[str]:
        ranked = sorted(variable_scores.items(), key=lambda item: item[1])[:3]
        return [self.variable_names.get(code, code) for code, _ in ranked]


def score_decoded_responses(responses: list[DecodedResponse], product_lock: ProductLock | None = None) -> list[ScoredOrganisation]:
    engine = ScoringEngine(product_lock=product_lock)
    return engine.score_responses(responses)
