from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.limesurvey_decoder import DecodedResponse
from engine.scoring_engine import ScoredOrganisation


class ReportDataBuilderError(Exception):
    """Raised when report-data payloads cannot be built safely."""


def build_report_data_bundle(
    decoded_responses: list[DecodedResponse],
    scored_organisations: list[ScoredOrganisation],
) -> list[dict[str, Any]]:
    if len(decoded_responses) != len(scored_organisations):
        raise ReportDataBuilderError("Decoded responses and scored organisations must be aligned.")

    bundle: list[dict[str, Any]] = []
    for decoded, scored in zip(decoded_responses, scored_organisations, strict=True):
        bundle.append(_build_report_payload(decoded, scored))
    return bundle


def write_report_data_bundle(
    decoded_responses: list[DecodedResponse],
    scored_organisations: list[ScoredOrganisation],
    output_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    bundle = build_report_data_bundle(decoded_responses, scored_organisations)
    target_dir = Path(output_dir) if output_dir is not None else Path("outputs")
    target_dir.mkdir(parents=True, exist_ok=True)

    payload_path = target_dir / "report_data.json"
    payload_path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    return bundle


def _build_report_payload(decoded: DecodedResponse, scored: ScoredOrganisation) -> dict[str, Any]:
    protected_evidence = _detect_protected_evidence(decoded)
    unsafe_route = _detect_unsafe_route(decoded)
    manual_review_flags = _manual_review_flags(decoded, protected_evidence, unsafe_route)

    return {
        "organisation_profile": {
            "name": decoded.organisation_name,
            "decoded_scored_signal_count": decoded.decoded_scored_signals,
        },
        "overall_score": scored.overall_readiness_score,
        "result_band": scored.result_band,
        "variable_scores": scored.variable_scores,
        "assessment_area_scores": scored.driver_scores,
        "journey_stage_scores": _journey_stage_scores(scored),
        "breakpoint_stage": _breakpoint_stage(decoded, scored),
        "top_repair_priorities": scored.top_repair_priorities[:5],
        "protected_evidence_flag": protected_evidence,
        "unsafe_route_flag": unsafe_route,
        "manual_review_flags": manual_review_flags,
        "free_report_visibility": {
            "protected_evidence_detail": not protected_evidence,
            "unsafe_route_detail": not unsafe_route,
            "full_detail": False,
        },
        "full_report_visibility": {
            "protected_evidence_detail": True,
            "unsafe_route_detail": True,
            "full_detail": True,
        },
        "decoded_scored_signal_count": decoded.decoded_scored_signals,
    }


def _detect_protected_evidence(decoded: DecodedResponse) -> bool:
    text = " ".join(str(value) for row in decoded.raw_rows for value in row.values() if value is not None)
    lowered = text.lower()
    return any(token in lowered for token in ["protected", "sensitive", "repressed", "confidential"])


def _detect_unsafe_route(decoded: DecodedResponse) -> bool:
    text = " ".join(str(value) for row in decoded.raw_rows for value in row.values() if value is not None)
    lowered = text.lower()
    return any(token in lowered for token in ["unsafe", "direct route", "route repair", "manual review"])


def _manual_review_flags(decoded: DecodedResponse, protected_evidence: bool, unsafe_route: bool) -> list[str]:
    flags: list[str] = []
    if protected_evidence:
        flags.append("protected evidence requires review")
    if unsafe_route:
        flags.append("unsafe route requires manual review")
    if not flags:
        flags.append("no manual review required")
    return flags


def _journey_stage_scores(scored: ScoredOrganisation) -> dict[str, float]:
    return {
        "stage_1": scored.overall_readiness_score * 0.5,
        "stage_2": scored.overall_readiness_score * 0.7,
        "stage_3": scored.overall_readiness_score * 0.8,
        "stage_4": scored.overall_readiness_score * 0.9,
        "stage_5": scored.overall_readiness_score,
    }


def _breakpoint_stage(decoded: DecodedResponse, scored: ScoredOrganisation) -> str:
    if scored.overall_readiness_score >= 75:
        return "7 Budget / Contract"
    if scored.overall_readiness_score >= 50:
        return "5 Conversation / Clarification"
    return "1 Opportunity Found"
