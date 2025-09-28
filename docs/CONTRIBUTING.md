# Contributing to Unified Lighting Analyzer

Thank you for your interest in contributing to the Unified Lighting Analyzer! This document provides guidelines and information for contributors.

## 📋 Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Contributing Guidelines](#contributing-guidelines)
5. [Code Style](#code-style)
6. [Testing](#testing)
7. [Documentation](#documentation)
8. [Submitting Changes](#submitting-changes)
9. [Areas for Contribution](#areas-for-contribution)

## 🤝 Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. By participating, you agree to:

- Be respectful and inclusive
- Focus on constructive feedback
- Respect different viewpoints and experiences
- Accept responsibility for your actions
- Help create a harassment-free environment

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+**
- **Git**
- **GitHub account**
- **Basic knowledge** of Python, lighting standards, and PDF processing

### Fork and Clone

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/your-username/unified-lighting-analyzer.git
   cd unified-lighting-analyzer
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/original-owner/unified-lighting-analyzer.git
   ```

## 🛠️ Development Setup

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .
```

### 3. Verify Setup

```bash
# Run tests
python -m pytest tests/

# Run linting
black src/
flake8 src/
mypy src/

# Test the application
python main.py --help
```

## 📝 Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

- **🐛 Bug fixes**: Fix issues and improve reliability
- **✨ New features**: Add new functionality and capabilities
- **📚 Documentation**: Improve guides, API docs, and examples
- **🧪 Tests**: Add or improve test coverage
- **🎨 UI/UX**: Enhance the web interface and user experience
- **⚡ Performance**: Optimize code and improve speed
- **🔧 Refactoring**: Improve code structure and maintainability

### Contribution Process

1. **Check existing issues** and pull requests
2. **Create an issue** for significant changes
3. **Fork and create a feature branch**
4. **Make your changes** following our guidelines
5. **Add tests** for new functionality
6. **Update documentation** as needed
7. **Submit a pull request**

### Branch Naming

Use descriptive branch names:

```bash
# Feature branches
feature/add-new-extraction-method
feature/enhance-standards-support
feature/improve-web-interface

# Bug fix branches
fix/area-extraction-issue
fix/import-error-handling
fix/memory-leak-in-ocr

# Documentation branches
docs/update-api-reference
docs/add-user-examples
docs/improve-installation-guide
```

## 🎨 Code Style

### Python Style Guide

We follow **PEP 8** with some modifications:

```python
# Use type hints for all functions
def extract_data(pdf_path: Union[str, Path]) -> ExtractionResult:
    """Extract data from PDF with comprehensive error handling."""
    pass

# Use descriptive variable names
room_illuminance_average = 520.0
compliance_check_results = []

# Use docstrings for all classes and methods
class FastDialuxAnalyzer:
    """
    Fast analyzer for Dialux reports with focused extraction.
    
    This analyzer provides quick analysis using regex patterns
    and optional OpenAI enhancement for company information.
    """
    
    def analyze_dialux_report(self, pdf_path: Union[str, Path]) -> FastDialuxAnalysisResult:
        """
        Analyze Dialux report with fast extraction method.
        
        Args:
            pdf_path: Path to the PDF file to analyze
            
        Returns:
            FastDialuxAnalysisResult with comprehensive analysis
            
        Raises:
            DialuxAnalysisError: If analysis fails
        """
        pass
```

### Code Formatting

We use **Black** for code formatting:

```bash
# Format code
black src/ tests/

# Check formatting
black --check src/ tests/
```

### Import Organization

```python
# Standard library imports
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union

# Third-party imports
import pandas as pd
import streamlit as st
from dataclasses import dataclass

# Local imports
from .core.config import config
from .extractors.pdf_extractor import PDFExtractor
```

### Error Handling

```python
# Use specific exceptions
try:
    result = extractor.extract_data(pdf_path)
except PDFExtractionError as e:
    logger.error(f"PDF extraction failed: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise DialuxAnalysisError(f"Analysis failed: {e}")
```

## 🧪 Testing

### Test Structure

```bash
tests/
├── unit/                    # Unit tests
│   ├── test_extractors.py
│   ├── test_analyzers.py
│   └── test_standards.py
├── integration/             # Integration tests
│   ├── test_web_interface.py
│   └── test_cli.py
├── fixtures/                # Test data
│   ├── sample_reports/
│   └── expected_results/
└── conftest.py             # Test configuration
```

### Writing Tests

```python
import pytest
from pathlib import Path
from src.analyzers.fast_dialux_analyzer import FastDialuxAnalyzer

class TestFastDialuxAnalyzer:
    """Test suite for FastDialuxAnalyzer."""
    
    def test_analyze_dialux_report_success(self, sample_pdf_path):
        """Test successful analysis of Dialux report."""
        analyzer = FastDialuxAnalyzer()
        result = analyzer.analyze_dialux_report(sample_pdf_path)
        
        assert result.report is not None
        assert result.report.total_rooms > 0
        assert result.report.total_area > 0
        assert len(result.recommendations) > 0
    
    def test_analyze_dialux_report_invalid_file(self):
        """Test analysis with invalid file path."""
        analyzer = FastDialuxAnalyzer()
        
        with pytest.raises(DialuxAnalysisError):
            analyzer.analyze_dialux_report("nonexistent.pdf")
    
    @pytest.mark.parametrize("room_type,expected_standard", [
        ("office", "EN_12464_1"),
        ("meeting_room", "EN_12464_1"),
        ("corridor", "EN_12464_1"),
    ])
    def test_room_type_mapping(self, room_type, expected_standard):
        """Test room type to standard mapping."""
        analyzer = FastDialuxAnalyzer()
        # Test implementation
        pass
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/unit/test_analyzers.py

# Run with coverage
python -m pytest --cov=src tests/

# Run with verbose output
python -m pytest -v

# Run specific test
python -m pytest tests/unit/test_analyzers.py::TestFastDialuxAnalyzer::test_analyze_dialux_report_success
```

### Test Data

Create test fixtures in `tests/fixtures/`:

```python
# conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def sample_pdf_path():
    """Path to sample PDF for testing."""
    return Path("tests/fixtures/sample_reports/test_report.pdf")

@pytest.fixture
def expected_analysis_result():
    """Expected analysis result for comparison."""
    return {
        "project_name": "Test Project",
        "total_rooms": 3,
        "total_area": 150.0,
        "overall_compliance_rate": 0.85
    }
```

## 📚 Documentation

### Documentation Standards

- **Docstrings**: Use Google-style docstrings
- **Type hints**: Include for all functions and methods
- **Examples**: Provide usage examples where helpful
- **Error handling**: Document possible exceptions

### Docstring Format

```python
def extract_room_data(text: str, room_name: str) -> Dict[str, Any]:
    """
    Extract room data from text using regex patterns.
    
    Args:
        text: Raw text from PDF containing room information
        room_name: Name of the room to extract data for
        
    Returns:
        Dictionary containing room data with keys:
        - area: Room area in square meters
        - illuminance_avg: Average illuminance in lux
        - uniformity: Uniformity ratio
        - ugr: Unified Glare Rating
        
    Raises:
        ValueError: If room_name is empty or invalid
        ExtractionError: If room data cannot be extracted
        
    Example:
        >>> text = "Office 1: Area 50 m², Illuminance 520 lux"
        >>> data = extract_room_data(text, "Office 1")
        >>> print(data['area'])
        50.0
    """
    pass
```

### Updating Documentation

When adding new features:

1. **Update README.md** if it's a major feature
2. **Update API_REFERENCE.md** for new classes/methods
3. **Update USER_GUIDE.md** for user-facing changes
4. **Add examples** to relevant documentation files

## 📤 Submitting Changes

### Pull Request Process

1. **Create a feature branch** from `main`
2. **Make your changes** following our guidelines
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Run all tests** and ensure they pass
6. **Create a pull request** with a clear description

### Pull Request Template

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows the project's style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)

## Related Issues
Closes #(issue number)
```

### Review Process

1. **Automated checks** must pass (tests, linting, formatting)
2. **Code review** by maintainers
3. **Testing** on different platforms
4. **Documentation review**
5. **Approval and merge**

## 🎯 Areas for Contribution

### High Priority

- **New extraction methods** for different PDF formats
- **Additional standards** support (IES, ASHRAE, etc.)
- **Performance optimizations** for large PDFs
- **Enhanced error handling** and user feedback
- **Test coverage** improvements

### Medium Priority

- **UI/UX improvements** for the web interface
- **Export functionality** enhancements
- **Batch processing** capabilities
- **API improvements** and new endpoints
- **Documentation** improvements

### Low Priority

- **Code refactoring** and cleanup
- **Additional language support** for OCR
- **Advanced visualization** features
- **Integration** with other tools
- **Mobile responsiveness** improvements

### Specific Issues

Check our [GitHub Issues](https://github.com/your-username/unified-lighting-analyzer/issues) for:

- **Good first issues**: Labeled for new contributors
- **Help wanted**: Community contributions needed
- **Bug reports**: Issues to fix
- **Feature requests**: New functionality ideas

## 🏷️ Labels and Milestones

### Issue Labels

- **bug**: Something isn't working
- **enhancement**: New feature or request
- **documentation**: Improvements to documentation
- **good first issue**: Good for newcomers
- **help wanted**: Extra attention is needed
- **priority: high**: High priority issues
- **priority: medium**: Medium priority issues
- **priority: low**: Low priority issues

### Pull Request Labels

- **ready for review**: Ready for maintainer review
- **needs testing**: Requires additional testing
- **needs documentation**: Documentation updates needed
- **breaking change**: Contains breaking changes

## 📞 Getting Help

### Communication Channels

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: [Scc@shortcircuitcompany.com](mailto:Scc@shortcircuitcompany.com)

### Before Asking for Help

1. **Check existing issues** and discussions
2. **Read the documentation** thoroughly
3. **Try to reproduce** the issue
4. **Provide detailed information** about your environment

### Asking Good Questions

When asking for help, include:

- **Environment details**: OS, Python version, package versions
- **Steps to reproduce**: Clear steps to reproduce the issue
- **Expected vs actual behavior**: What you expected vs what happened
- **Error messages**: Full error messages and stack traces
- **Code examples**: Minimal code that demonstrates the issue

## 🎉 Recognition

Contributors will be recognized in:

- **README.md**: List of contributors
- **Release notes**: Credit for contributions
- **GitHub**: Contributor statistics
- **Documentation**: Credit in relevant sections

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

**Thank you for contributing to the Unified Lighting Analyzer! Your contributions help make lighting analysis more accessible and accurate for professionals worldwide.**

**For questions about contributing, contact [Short Circuit Company](mailto:Scc@shortcircuitcompany.com).**
