from __future__ import annotations

from pathlib import Path
from typing import Any

# Try to import weasyprint; if not available, gracefully degrade
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False


class PDFReportRendererError(Exception):
    """Raised when PDF rendering fails."""


def render_pdf_report(html_content: str, output_path: str | Path) -> dict[str, Any]:
    """
    Render PDF from HTML content.

    Args:
        html_content: HTML string from HTML report renderer
        output_path: Path to write PDF file

    Returns:
        Dictionary with status and result

    Raises:
        PDFReportRendererError: If critical error occurs
    """
    target_path = Path(output_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if not WEASYPRINT_AVAILABLE:
        return {
            "status": "PDF_RENDER_ERROR",
            "message": "weasyprint not available; PDF rendering skipped",
            "html_rendered": True,
            "pdf_path": None,
        }

    try:
        # Render HTML to PDF using weasyprint
        pdf_html = HTML(string=html_content, base_url=str(target_path.parent))
        pdf_html.write_pdf(str(target_path))

        return {
            "status": "PDF_RENDERED",
            "message": "PDF successfully rendered from HTML",
            "html_rendered": True,
            "pdf_path": str(target_path),
        }
    except Exception as e:
        # Log the error but don't fail the entire process
        return {
            "status": "PDF_RENDER_ERROR",
            "message": f"PDF rendering failed: {str(e)}",
            "html_rendered": True,
            "pdf_path": None,
            "error_detail": str(e),
        }


def is_pdf_rendering_available() -> bool:
    """
    Check if PDF rendering is available.

    Returns True if weasyprint is installed and functional.
    """
    return WEASYPRINT_AVAILABLE
