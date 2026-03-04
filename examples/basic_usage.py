"""
Minimal example of using ecovadis_toolkit for scoring,
compliance checking, and report generation.
"""

from datetime import date

from ecovadis_toolkit.scorer import EcoVadisScorer, ThemeScoreInput
from ecovadis_toolkit.compliance import (
    DocumentMetadata,
    ComplianceChecker,
)
from ecovadis_toolkit.report_generator import ReportGenerator


def main() -> None:
    # 1. Prepare scoring inputs
    scorer = EcoVadisScorer()
    theme_inputs = [
        ThemeScoreInput(theme="Environment", score=65.0, weight=25.0),
        ThemeScoreInput(theme="Labor & Human Rights", score=70.0, weight=25.0),
        ThemeScoreInput(theme="Ethics", score=60.0, weight=25.0),
        ThemeScoreInput(theme="Sustainable Procurement", score=55.0, weight=25.0),
    ]
    score_result = scorer.calculate_overall_score(theme_inputs)

    # 2. Prepare simple document inventory
    documents = {
        "env_policy": DocumentMetadata(
            name="Environmental Policy",
            theme="Environment",
            iso_clause="5.2",
            last_updated=date(2025, 1, 10),
            owner="HSE Manager",
        ),
        "code_of_conduct": DocumentMetadata(
            name="Code of Conduct",
            theme="Ethics",
            iso_clause=None,
            last_updated=date(2023, 6, 1),
            owner="HR",
        ),
    }

    requirements = [
        {
            "id": "ENV-001",
            "description": "Documented environmental policy approved by top management.",
            "theme": "Environment",
            "doc_id": "env_policy",
            "iso_clause": "5.2",
        },
        {
            "id": "ETH-001",
            "description": "Code of conduct covering anti-corruption.",
            "theme": "Ethics",
            "doc_id": "code_of_conduct",
            "iso_clause": None,
        },
        {
            "id": "LAB-001",
            "description": "Human rights policy aligned with UNGPs.",
            "theme": "Labor & Human Rights",
            "doc_id": "hr_policy",
            "iso_clause": None,
        },
    ]

    checker = ComplianceChecker(documents)
    compliance_results = checker.check_required_documents(requirements)

    # 3. Generate a Markdown report
    generator = ReportGenerator(
        company_name="FABTECH International",
        metadata={"location": "Dubai, UAE"},
    )
    md_report = generator.generate_markdown_report(score_result, compliance_results)

    print(md_report)


if __name__ == "__main__":
    main()
