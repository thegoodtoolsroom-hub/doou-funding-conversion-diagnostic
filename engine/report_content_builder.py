from __future__ import annotations

from typing import Any


class ReportContentBuilderError(Exception):
    """Raised when report content cannot be safely built."""


def build_report_content(report_data: dict[str, Any], report_variant: str = "full") -> dict[str, Any]:
    """
    Transform report_data.json payload into structured content for HTML/PDF rendering.

    This ensures that report content is deterministic, branded, and ready for template
    rendering without relying on Word section injection or placeholder text.

    Args:
        report_data: Dictionary from report_data.json

    Returns:
        Dictionary with structured content for all report sections

    Raises:
        ReportContentBuilderError: If report_data is missing critical fields
    """
    if not isinstance(report_data, dict):
        raise ReportContentBuilderError("report_data must be a dictionary")

    variant = report_variant.lower()
    if variant not in {"full", "free"}:
        raise ReportContentBuilderError("report_variant must be 'full' or 'free'")

    org_profile = report_data.get("organisation_profile", {})
    org_name = org_profile.get("name", "Unknown Organisation")
    decoded_signal_count = report_data.get("decoded_scored_signal_count", 0)

    if decoded_signal_count <= 0:
        raise ReportContentBuilderError(
            f"Cannot render report for {org_name}: no decoded scored signals available"
        )

    overall_score = float(report_data.get("overall_score", 0))
    result_band = report_data.get("result_band", "Unknown")
    variable_scores = report_data.get("variable_scores", {}) or {}
    assessment_area_scores = report_data.get("assessment_area_scores", {}) or {}
    journey_stage_scores = report_data.get("journey_stage_scores", {}) or {}
    breakpoint_stage = report_data.get("breakpoint_stage", "Unknown")
    top_repair_priorities = report_data.get("top_repair_priorities", []) or []

    protected_evidence_flag = report_data.get("protected_evidence_flag", False)
    unsafe_route_flag = report_data.get("unsafe_route_flag", False)
    manual_review_flags = report_data.get("manual_review_flags", []) or []
    actionable_manual_review_flags = [
        flag for flag in manual_review_flags if _is_actionable_manual_review_flag(flag)
    ]
    manual_review_required = bool(actionable_manual_review_flags)

    free_visibility = report_data.get("free_report_visibility", {}) or {}
    full_visibility = report_data.get("full_report_visibility", {}) or {}

    # Compute diagnostic confidence score
    confidence_score = _calculate_diagnostic_confidence(decoded_signal_count, variable_scores)

    # Build variable scores with labels
    variable_scores_labeled = _label_variable_scores(variable_scores)

    # Build assessment area scores with labels
    assessment_area_scores_labeled = _label_assessment_area_scores(assessment_area_scores)

    # Build journey stage scores
    journey_stage_scores_labeled = _label_journey_stage_scores(journey_stage_scores)

    # Prepare visibility settings for template.
    is_free_report = variant == "free"
    visibility = free_visibility if is_free_report else full_visibility
    show_protected_evidence_detail = visibility.get(
        "protected_evidence_detail",
        False if is_free_report else True,
    )
    show_unsafe_route_detail = visibility.get(
        "unsafe_route_detail",
        False if is_free_report else True,
    )
    visible_manual_review_flags = [] if is_free_report else actionable_manual_review_flags
    report_generated_label = str(
        report_data.get("report_generated_label")
        or report_data.get("report_generated_date")
        or report_data.get("report_generated_at")
        or "from report_data.json"
    )

    return {
        "organisation_name": org_name,
        "overall_score": round(overall_score, 2),
        "result_band": result_band,
        "diagnostic_confidence_score": confidence_score,
        "decoded_signal_count": decoded_signal_count,
        "variable_scores": variable_scores_labeled,
        "assessment_area_scores": assessment_area_scores_labeled,
        "journey_stage_scores": journey_stage_scores_labeled,
        "breakpoint_stage": breakpoint_stage,
        "top_repair_priorities": top_repair_priorities,
        "protected_evidence_flag": protected_evidence_flag,
        "unsafe_route_flag": unsafe_route_flag,
        "manual_review_flags": manual_review_flags,
        "visible_manual_review_flags": visible_manual_review_flags,
        "manual_review_required": manual_review_required,
        "is_free_report": is_free_report,
        "show_protected_evidence_detail": show_protected_evidence_detail,
        "show_unsafe_route_detail": show_unsafe_route_detail,
        "report_generated_label": report_generated_label,
        "report_generated": True,
    }


def _is_actionable_manual_review_flag(flag: Any) -> bool:
    lowered = str(flag).strip().lower()
    if not lowered or lowered == "no manual review required":
        return False
    return any(
        token in lowered
        for token in ("manual review", "requires review", "protected evidence", "unsafe route")
    )


def _calculate_diagnostic_confidence(signal_count: int, variable_scores: dict[str, float]) -> int:
    """
    Calculate diagnostic confidence (0-100) based on signal count and score spread.

    Confidence increases with:
    - More decoded signals (up to 200+)
    - Wider spread of variable scores (not all 50%)
    """
    # Base confidence on signal count (max at 200+)
    if signal_count >= 200:
        signal_confidence = 90
    elif signal_count >= 150:
        signal_confidence = 75
    elif signal_count >= 100:
        signal_confidence = 60
    elif signal_count >= 50:
        signal_confidence = 40
    else:
        signal_confidence = 20

    # Adjust based on score spread
    if variable_scores:
        scores_list = list(variable_scores.values())
        avg_score = sum(scores_list) / len(scores_list)
        spread = max(scores_list) - min(scores_list)

        if spread >= 50:
            spread_confidence = 95
        elif spread >= 30:
            spread_confidence = 85
        elif spread >= 15:
            spread_confidence = 70
        else:
            spread_confidence = 50

        # Weighted average: 60% signal count, 40% score spread
        confidence = int(signal_confidence * 0.6 + spread_confidence * 0.4)
    else:
        confidence = signal_confidence

    return min(100, max(0, confidence))


def _label_variable_scores(variable_scores: dict[str, float]) -> list[dict[str, Any]]:
    """Convert variable scores dict to labeled list with descriptions."""
    variable_labels = {
        "R01": "Financial Records and Controls",
        "R02": "Financial Planning and Forecasting",
        "R03": "Income and Revenue Security",
        "R04": "Governance and Oversight",
        "R05": "Grant Management Readiness",
        "R06": "Finance and Risk Readiness",
        "R07": "Strategic Planning",
        "R08": "Organisational Sustainability",
        "R09": "Safeguarding and Ethics",
        "R10": "Protected Evidence Protocol",
        "R11": "Document Readiness",
        "R12": "Evidence Quality and Presentation",
    }

    result = []
    for code in ["R01", "R02", "R03", "R04", "R05", "R06", "R07", "R08", "R09", "R10", "R11", "R12"]:
        score = variable_scores.get(code, 0)
        result.append({
            "code": code,
            "label": variable_labels.get(code, f"Variable {code}"),
            "score": round(score, 2),
        })
    return result


def _label_assessment_area_scores(assessment_area_scores: dict[str, float]) -> list[dict[str, Any]]:
    """Convert assessment area scores dict to labeled list with descriptions."""
    area_labels = {
        "D01": "Financial Records and Controls",
        "D02": "Bank Account Management",
        "D03": "Cash Flow and Liquidity",
        "D04": "Budget and Forecast Accuracy",
        "D05": "Income Security and Diversification",
        "D06": "Organisational Leadership",
        "D07": "Board and Governance Structure",
        "D08": "Risk and Compliance Management",
        "D09": "Grant Proposal Development",
        "D10": "Grant Monitoring and Reporting",
        "D11": "Grant Transition and Renewal",
        "D12": "Sustainability Strategy",
        "D13": "Growth and Adaptation Planning",
        "D14": "Staff Capacity and Development",
        "D15": "Safeguarding Policies",
        "D16": "Ethics and Integrity",
        "D17": "Community Engagement",
        "D18": "Beneficiary Impact Measurement",
        "D19": "Protected Evidence Protocol",
        "D20": "Document and Compliance Files",
        "D21": "Evidence of Income",
        "D22": "Evidence of Expenditure",
        "D23": "Evidence of Beneficiary Impact",
        "D24": "Evidence of Strategic Direction",
    }

    result = []
    for i in range(1, 25):
        code = f"D{i:02d}"
        score = assessment_area_scores.get(code, 0)
        result.append({
            "code": code,
            "label": area_labels.get(code, f"Assessment Area {code}"),
            "score": round(score, 2),
        })
    return result


def _label_journey_stage_scores(journey_stage_scores: dict[str, float]) -> list[dict[str, Any]]:
    """Convert journey stage scores to labeled list."""
    stage_labels = {
        "stage_1": "Stage 1: Readiness Check",
        "stage_2": "Stage 2: Foundation Building",
        "stage_3": "Stage 3: Capability Development",
        "stage_4": "Stage 4: Advanced Preparation",
        "stage_5": "Stage 5: Conversation / Clarification",
    }

    result = []
    for stage_key in ["stage_1", "stage_2", "stage_3", "stage_4", "stage_5"]:
        score = journey_stage_scores.get(stage_key, 0)
        result.append({
            "stage": stage_key,
            "label": stage_labels.get(stage_key, stage_key),
            "score": round(score, 2),
        })
    return result
