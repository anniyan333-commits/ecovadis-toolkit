"""
Report generation utilities for EcoVadis assessments and ISO 14001 tracking.

This module is intentionally lightweight and dependency-free by default:
- It accepts plain Python data structures (scores, compliance checks)
- It can export simple text, Markdown, or JSON reports
"""

from dataclasses import asdict
from typing import Any, Dict, List, Optional
import json
from datetime import datetime

from .scorer import EcoVadisScoreResult
from .compliance import ComplianceCheckResult


class ReportGenerator:
    """
    Turn scoring and compliance data into human-readable output.

    Typical flow:
    - Run scorer to get EcoVadisScoreResult
    - Run ComplianceChecker to get ComplianceCheckResult list
    - Feed both into this class and generate a report string or JSON
    """

    def __init__(
        self,
        company_name: str,
        assessment_year: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.company_name = company_name
        self.assessment_year = assessment_year or datetime.utcnow().year
        self.metadata = metadata or {}

    def generate_markdown_report(
        self,
        score_result: EcoVadisScoreResult,
        compliance_results: List[ComplianceCheckResult],
    ) -> str:
        """Return a Markdown report suitable for README, Confluence, or EcoVadis prep."""
        lines: List[str] = []

        lines.append(f"# EcoVadis Assessment Summary - {self.company_name}")
        lines.append("")
        lines.append(f"Assessment year: **{self.assessment_year}**")
        lines.append("")
        if self.metadata:
            lines.append("## Context")
            for k, v in self.metadata.items():
                lines.append(f"- {k}: {v}")
            lines.append("")

        # Scores
        lines.append("## EcoVadis scores by theme")
        lines.append("")
        lines.append("| Theme | Score | Weight | Weighted score |")
        lines.append("|-------|-------|--------|----------------|")
        for theme_score in score_result.theme_scores:
            lines.append(
                f"| {theme_score.theme} | {theme_score.score:.1f} | "
                f"{theme_score.weight:.0f}% | {theme_score.weighted_score:.1f} |"
            )
        lines.append("")
        lines.append(f"**Overall score:** {score_result.overall_score:.1f}")
        lines.append("")

        # Compliance
        lines.append("## Compliance checks")
        lines.append("")
        lines.append("| Requirement | Theme | ISO clause | Status | Details |")
        lines.append("|------------|-------|-----------|--------|---------|")
        for res in compliance_results:
            iso_clause = res.iso_clause or ""
            details = res.details.replace("|", "\\|")
            lines.append(
                f"| {res.requirement_id} - {res.description} | "
                f"{res.theme} | {iso_clause} | {res.status} | {details} |"
            )

        return "\n".join(lines)

    def generate_json_report(
        self,
        score_result: EcoVadisScoreResult,
        compliance_results: List[ComplianceCheckResult],
    ) -> str:
        """Return a JSON string with scores and compliance details."""
        payload = {
            "company_name": self.company_name,
            "assessment_year": self.assessment_year,
            "metadata": self.metadata,
            "scores": {
                "overall_score": score_result.overall_score,
                "theme_scores": [
                    {
                        "theme": ts.theme,
                        "score": ts.score,
                        "weight": ts.weight,
                        "weighted_score": ts.weighted_score,
                    }
                    for ts in score_result.theme_scores
                ],
            },
            "compliance": [asdict(r) for r in compliance_results],
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }
        return json.dumps(payload, indent=2)
