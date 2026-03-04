"""
EcoVadis Toolkit - Open source Python library for EcoVadis sustainability assessment automation.

This library provides tools for:
- Automated scoring and gap analysis
- Compliance checklist management
- Evidence document tracking
- Report generation
- Action plan prioritization
"""

__version__ = "0.1.0"
__author__ = "EcoVadis Toolkit Contributors"
__license__ = "MIT"

from ecovadis_toolkit.scorer import EcoVadisScorer
from ecovadis_toolkit.compliance import ComplianceChecker
from ecovadis_toolkit.report_generator import ReportGenerator

__all__ = [
    "EcoVadisScorer",
    "ComplianceChecker",
    "ReportGenerator",
    "__version__",
]
