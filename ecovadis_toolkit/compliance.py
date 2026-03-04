"""
Compliance utilities for EcoVadis, ISO 14001 and supply chain due diligence.

This module focuses on:
- Checking presence and freshness of key policies and procedures
- Mapping internal documents to EcoVadis themes and ISO 14001 clauses
- Producing simple, machine-readable compliance gaps for further reporting
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional, Any


ECOVADIS_THEMES = (
    "Environment",
    "Labor & Human Rights",
    "Ethics",
    "Sustainable Procurement",
)


@dataclass
class DocumentMetadata:
    name: str
    theme: str
    iso_clause: Optional[str] = None
    last_updated: Optional[date] = None
    owner: Optional[str] = None
    url: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplianceCheckResult:
    requirement_id: str
    description: str
    theme: str
    iso_clause: Optional[str]
    status: str  # "compliant", "partial", "missing"
    details: str


class ComplianceChecker:
    """
    Simple rule-based compliance checker.

    You pass:
    - a dictionary of documents keyed by an internal ID
    - a list of requirements describing what should exist

    It returns:
    - structured ComplianceCheckResult objects that can be fed to report_generator
    """

    def __init__(self, documents: Dict[str, DocumentMetadata]):
        self.documents = documents

    def check_required_documents(
        self,
        requirements: List[Dict[str, Any]],
        freshness_years: int = 2,
    ) -> List[ComplianceCheckResult]:
        """
        Run basic presence + freshness checks against required documents.

        requirements: list of dicts with keys:
          - id: unique requirement id
          - description: human readable requirement
          - theme: one of ECOVADIS_THEMES
          - doc_id: key expected in self.documents
          - iso_clause: optional ISO 14001 or other clause reference
        """
        results: List[ComplianceCheckResult] = []

        for req in requirements:
            doc_id = req.get("doc_id")
            doc = self.documents.get(doc_id)

            if doc is None:
                results.append(
                    ComplianceCheckResult(
                        requirement_id=req["id"],
                        description=req["description"],
                        theme=req["theme"],
                        iso_clause=req.get("iso_clause"),
                        status="missing",
                        details=f"Document with id '{doc_id}' not found.",
                    )
                )
                continue

            status = "compliant"
            details_parts = [f"Document '{doc.name}' found."]

            # Freshness check
            if doc.last_updated is not None:
                age_years = (date.today() - doc.last_updated).days / 365.25
                if age_years > freshness_years:
                    status = "partial"
                    details_parts.append(
                        f"Last updated {age_years:.1f} years ago; "
                        f"threshold is {freshness_years} years."
                    )
            else:
                status = "partial"
                details_parts.append("No last_updated date provided.")

            # Theme alignment
            if doc.theme != req["theme"]:
                status = "partial"
                details_parts.append(
                    f"Theme mismatch: expected '{req['theme']}', got '{doc.theme}'."
                )

            results.append(
                ComplianceCheckResult(
                    requirement_id=req["id"],
                    description=req["description"],
                    theme=req["theme"],
                    iso_clause=req.get("iso_clause"),
                    status=status,
                    details=" ".join(details_parts),
                )
            )

        return results
