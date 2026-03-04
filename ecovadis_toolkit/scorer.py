"""
EcoVadis Scorer - Automated scoring and gap analysis for EcoVadis assessments.

This module provides tools to calculate EcoVadis scores, identify gaps,
and prioritize improvement actions across the four EcoVadis themes:
Environment, Labor & Human Rights, Ethics, and Sustainable Procurement.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class EcoVadisTheme(Enum):
    ENVIRONMENT = "environment"
    LABOR_HUMAN_RIGHTS = "labor_human_rights"
    ETHICS = "ethics"
    SUSTAINABLE_PROCUREMENT = "sustainable_procurement"


THEME_WEIGHTS = {
    EcoVadisTheme.ENVIRONMENT: 0.30,
    EcoVadisTheme.LABOR_HUMAN_RIGHTS: 0.40,
    EcoVadisTheme.ETHICS: 0.15,
    EcoVadisTheme.SUSTAINABLE_PROCUREMENT: 0.15,
}

MEDAL_THRESHOLDS = {
    "platinum": 78,
    "gold": 62,
    "silver": 45,
    "bronze": 25,
}


@dataclass
class ThemeScore:
    theme: EcoVadisTheme
    score: float
    max_score: float = 100.0
    evidence_items: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)

    @property
    def percentage(self) -> float:
        return (self.score / self.max_score) * 100

    @property
    def gap_count(self) -> int:
        return len(self.gaps)


@dataclass
class AssessmentResult:
    company_name: str
    assessment_year: int
    theme_scores: Dict[EcoVadisTheme, ThemeScore] = field(default_factory=dict)

    @property
    def overall_score(self) -> float:
        if not self.theme_scores:
            return 0.0
        weighted_sum = sum(
            score.percentage * THEME_WEIGHTS[theme]
            for theme, score in self.theme_scores.items()
        )
        return round(weighted_sum, 1)

    @property
    def medal_level(self) -> str:
        score = self.overall_score
        for medal, threshold in MEDAL_THRESHOLDS.items():
            if score >= threshold:
                return medal
        return "none"

    @property
    def total_gaps(self) -> int:
        return sum(ts.gap_count for ts in self.theme_scores.values())


class EcoVadisScorer:
    """
    Main class for calculating and analyzing EcoVadis assessment scores.

    Example usage:
        scorer = EcoVadisScorer("ACME Corp", 2024)
        scorer.add_theme_score(EcoVadisTheme.ENVIRONMENT, 65, gaps=["ISO 14001 not certified"])
        scorer.add_theme_score(EcoVadisTheme.LABOR_HUMAN_RIGHTS, 70)
        result = scorer.calculate()
        print(f"Overall score: {result.overall_score}")
        print(f"Medal: {result.medal_level}")
    """

    def __init__(self, company_name: str, assessment_year: int = 2024):
        self.company_name = company_name
        self.assessment_year = assessment_year
        self._theme_data: Dict[EcoVadisTheme, dict] = {}

    def add_theme_score(
        self,
        theme: EcoVadisTheme,
        score: float,
        evidence_items: Optional[List[str]] = None,
        gaps: Optional[List[str]] = None,
    ) -> "EcoVadisScorer":
        """Add a score for a specific EcoVadis theme."""
        if not 0 <= score <= 100:
            raise ValueError(f"Score must be between 0 and 100, got {score}")
        self._theme_data[theme] = {
            "score": score,
            "evidence_items": evidence_items or [],
            "gaps": gaps or [],
        }
        return self

    def calculate(self) -> AssessmentResult:
        """Calculate the final assessment result."""
        result = AssessmentResult(
            company_name=self.company_name,
            assessment_year=self.assessment_year,
        )
        for theme, data in self._theme_data.items():
            result.theme_scores[theme] = ThemeScore(
                theme=theme,
                score=data["score"],
                evidence_items=data["evidence_items"],
                gaps=data["gaps"],
            )
        return result

    def get_improvement_priorities(self) -> List[Dict]:
        """Return improvement actions sorted by potential score impact."""
        priorities = []
        for theme, data in self._theme_data.items():
            weight = THEME_WEIGHTS[theme]
            current_score = data["score"]
            potential_gain = (100 - current_score) * weight
            for gap in data["gaps"]:
                priorities.append({
                    "theme": theme.value,
                    "gap": gap,
                    "potential_score_gain": round(potential_gain / max(len(data["gaps"]), 1), 2),
                    "priority": "high" if potential_gain > 10 else "medium" if potential_gain > 5 else "low",
                })
        return sorted(priorities, key=lambda x: x["potential_score_gain"], reverse=True)

    @staticmethod
    def benchmark_score(score: float, industry: str = "manufacturing") -> Dict:
        """Compare score against industry benchmarks."""
        benchmarks = {
            "manufacturing": {"average": 45, "top_quartile": 62, "percentile_75": 58},
            "services": {"average": 48, "top_quartile": 65, "percentile_75": 60},
            "retail": {"average": 42, "top_quartile": 60, "percentile_75": 55},
        }
        bench = benchmarks.get(industry, benchmarks["manufacturing"])
        return {
            "score": score,
            "industry": industry,
            "industry_average": bench["average"],
            "above_average": score > bench["average"],
            "top_quartile": score >= bench["top_quartile"],
            "percentile_estimate": min(99, max(1, int((score / 100) * 100))),
        }
