from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from engine.report_content_builder import build_report_content, ReportContentBuilderError


class HTMLReportRendererError(Exception):
    """Raised when HTML report rendering fails."""


def render_html_report(
    report_data: dict[str, Any],
    output_path: str | Path | None = None,
    report_variant: str = "full",
) -> str:
    """
    Render a branded HTML report from report_data.json.

    Args:
        report_data: Dictionary from report_data.json
        output_path: Optional path to write HTML file
        report_variant: Either "full" or "free" visibility mode

    Returns:
        HTML string

    Raises:
        HTMLReportRendererError: If rendering fails
    """
    try:
        report_content = build_report_content(report_data, report_variant=report_variant)
    except ReportContentBuilderError as e:
        raise HTMLReportRendererError(f"Failed to build report content: {e}") from e

    try:
        env = _get_jinja_environment()
        template = env.get_template("report.html")
        html_output = template.render(**report_content)
    except Exception as e:
        raise HTMLReportRendererError(f"Failed to render Jinja2 template: {e}") from e

    if output_path is not None:
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            target_path.write_text(html_output, encoding="utf-8")
        except Exception as e:
            raise HTMLReportRendererError(f"Failed to write HTML to {output_path}: {e}") from e

    return html_output


def _get_jinja_environment() -> Environment:
    """
    Get Jinja2 environment configured for report templates.

    Searches for templates in templates/report_html/ relative to the package root.
    """
    # Find the templates directory
    template_dirs = [
        Path(__file__).resolve().parent.parent / "templates" / "report_html",
        Path("templates") / "report_html",
    ]

    template_dir = None
    for candidate in template_dirs:
        if candidate.exists():
            template_dir = str(candidate)
            break

    if template_dir is None:
        raise HTMLReportRendererError(
            f"Template directory not found. Searched: {template_dirs}"
        )

    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # Add custom filters
    env.filters["money"] = _filter_money
    env.filters["percentage"] = _filter_percentage
    env.filters["badge_class"] = _filter_badge_class
    env.filters["score_grade"] = _filter_score_grade

    return env


def _filter_money(value: float) -> str:
    """Format value as currency."""
    if not isinstance(value, (int, float)):
        return str(value)
    return f"${value:,.2f}"


def _filter_percentage(value: float) -> str:
    """Format value as percentage."""
    if not isinstance(value, (int, float)):
        return str(value)
    return f"{value:.1f}%"


def _filter_badge_class(score: float) -> str:
    """Return Bootstrap badge class based on score."""
    if score >= 75:
        return "badge-success"
    elif score >= 50:
        return "badge-warning"
    else:
        return "badge-danger"


def _filter_score_grade(score: float) -> str:
    """Return letter grade for score."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    elif score >= 50:
        return "E"
    else:
        return "F"
