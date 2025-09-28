"""
Setup script for Unified Lighting Analyzer
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = requirements_path.read_text().strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="unified-lighting-analyzer",
    version="1.0.0",
    author="AI Assistant",
    author_email="ai@example.com",
    description="A comprehensive system for analyzing lighting documents, standards, and Dialux reports",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-repo/unified-lighting-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.7.0",
        ],
        "ocr": [
            "pytesseract>=0.3.10",
            "opencv-python>=4.8.0",
            "pdf2image>=3.1.0",
        ],
        "tables": [
            "camelot-py[cv]>=0.10.1",
            "tabula-py>=2.7.0",
        ],
        "web": [
            "streamlit>=1.28.0",
            "plotly>=5.17.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "lighting-analyzer=main:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json", "*.yml", "*.yaml"],
    },
    keywords="lighting, standards, dialux, pdf, extraction, analysis, compliance",
    project_urls={
        "Bug Reports": "https://github.com/your-repo/unified-lighting-analyzer/issues",
        "Source": "https://github.com/your-repo/unified-lighting-analyzer",
        "Documentation": "https://github.com/your-repo/unified-lighting-analyzer/wiki",
    },
)
