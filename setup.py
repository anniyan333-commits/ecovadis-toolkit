from setuptools import setup, find_packages

setup(
    name="ecovadis-toolkit",
    version="0.1.0",
    description="Open-source Python toolkit for EcoVadis sustainability assessments, ESG scoring, ISO 14001 compliance tracking, and supply chain due diligence automation.",
    author="FABTECH International",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0,<3.0",
    ],
    python_requires=">=3.9",
)
