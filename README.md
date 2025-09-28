# Unified Lighting Analyzer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web%20Interface-red.svg)](https://streamlit.io/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green.svg)](https://openai.com/)

A comprehensive AI-powered system for analyzing lighting documents, standards compliance, and Dialux reports with intelligent data extraction and detailed recommendations.

**Developed by [Short Circuit Company](mailto:Scc@shortcircuitcompany.com)**

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Web Interface](#web-interface)
- [Command Line Interface](#command-line-interface)
- [Analysis Methods](#analysis-methods)
- [Standards Compliance](#standards-compliance)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Output Formats](#output-formats)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## 🎯 Overview

The Unified Lighting Analyzer combines the best features from multiple lighting analysis projects into a single, comprehensive solution. It provides intelligent PDF extraction, standards compliance checking, and detailed analysis reports for lighting professionals.

### Key Capabilities

- **Multi-method PDF extraction** with fallback strategies
- **Advanced table extraction** with quality analysis
- **Intelligent Dialux report analysis** with AI-powered extraction
- **Standards compliance checking** against EN 12464-1, BREEAM, and more
- **Comprehensive recommendations** with priority levels
- **Interactive web interface** with real-time results
- **Multiple export formats** for integration with other tools

## ✨ Features

### 🔍 **Intelligent PDF Extraction**
- **Multi-method extraction**: pdfplumber, PyMuPDF, pdfminer, OCR
- **Advanced table extraction**: Camelot, pdfplumber, OCR with quality filtering
- **Duplicate detection** and quality scoring
- **Lighting-specific pattern recognition**

### 🏢 **Dialux Report Analysis**
- **⚡ Fast Analysis**: Quick extraction with regex patterns
- **🤖 Enhanced Analysis**: OpenAI-powered comprehensive extraction
- **🔍 Standard Analysis**: Traditional multi-method approach
- **Company information extraction**: Project company, luminaire manufacturer, driver circuit company
- **Room-by-room analysis** with detailed parameters

### 📊 **Standards Compliance**
- **EN 12464-1:2021** compliance checking
- **BREEAM** compliance verification
- **Custom standards** support
- **Parameter-by-parameter comparison**
- **Compliance rate calculations**

### 💡 **Comprehensive Recommendations**
- **Categorized recommendations**: Illuminance, uniformity, glare, power efficiency
- **Priority levels**: Critical, high priority, moderate
- **Actionable suggestions** with specific values
- **Energy optimization** recommendations
- **Maintenance planning** guidance

### 🌐 **User Interface**
- **Interactive web interface** with Streamlit
- **Real-time analysis** with progress indicators
- **Detailed results display** with charts and tables
- **Export functionality** for reports
- **Responsive design** for all devices

## 🚀 Installation

### Prerequisites

- **Python 3.8+**
- **Java 8+** (required for Camelot table extraction)
- **Tesseract OCR** (for OCR functionality)

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/unified-lighting-analyzer.git
cd unified-lighting-analyzer
```

### Step 2: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# For minimal installation (core features only)
pip install -r requirements-minimal.txt
```

### Step 3: Install System Dependencies

#### Windows
```bash
# Install Tesseract OCR
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH: C:\Program Files\Tesseract-OCR

# Install Java (if not already installed)
# Download from: https://www.oracle.com/java/technologies/downloads/
```

#### macOS
```bash
# Install Tesseract OCR
brew install tesseract

# Install Java
brew install openjdk@11
```

#### Linux (Ubuntu/Debian)
```bash
# Install Tesseract OCR
sudo apt-get install tesseract-ocr

# Install Java
sudo apt-get install openjdk-11-jdk
```

### Step 4: Verify Installation

```bash
python -c "import streamlit, pdfplumber, camelot; print('✅ Installation successful!')"
```

## 🎯 Quick Start

### Web Interface (Recommended)

1. **Start the web interface**:
```bash
streamlit run web_app.py
```

2. **Open your browser** to `http://localhost:8501`

3. **Upload a PDF** and choose analysis method:
   - ⚡ **Fast Analysis** (Recommended) - Quick with area extraction
   - 🤖 **Enhanced Analysis** - OpenAI-powered comprehensive extraction
   - 🔍 **Standard Analysis** - Traditional multi-method approach

4. **View comprehensive results** with detailed analysis and recommendations

### Command Line Interface

```bash
# Fast analysis (recommended)
python main.py analyze-dialux-fast --input your_report.pdf

# Enhanced analysis with OpenAI
python main.py analyze-dialux-enhanced --input your_report.pdf --api-key your_openai_key

# Standard analysis
python main.py analyze-dialux --input your_report.pdf

# Web interface
python main.py web
```

## 🌐 Web Interface

The web interface provides an intuitive way to analyze lighting documents with real-time results and interactive visualizations.

### Navigation

- **🏠 Home**: Project overview and getting started
- **📄 PDF Extraction**: Basic PDF text and table extraction
- **📊 Table Analysis**: Advanced table extraction and analysis
- **📋 Standards Processing**: Lighting standards management
- **🏢 Dialux Analysis**: Comprehensive Dialux report analysis

### Analysis Methods

#### ⚡ Fast Analysis
- **Speed**: 2-5 seconds
- **Accuracy**: High for numerical data
- **Features**: Area extraction, company info, basic compliance
- **Best for**: Quick assessments and area verification

#### 🤖 Enhanced Analysis
- **Speed**: 10-30 seconds
- **Accuracy**: Very high with AI extraction
- **Features**: Comprehensive metadata, detailed company info, full analysis
- **Best for**: Complete project analysis and detailed reports

#### 🔍 Standard Analysis
- **Speed**: 30-60 seconds
- **Accuracy**: High with multiple extraction methods
- **Features**: Multi-method extraction, comprehensive analysis
- **Best for**: Complex PDFs and maximum compatibility

## 💻 Command Line Interface

### Basic Commands

```bash
# Show help
python main.py --help

# List available commands
python main.py --help

# Analyze Dialux report (fast)
python main.py analyze-dialux-fast --input report.pdf

# Analyze with OpenAI (enhanced)
python main.py analyze-dialux-enhanced --input report.pdf --api-key sk-...

# Standard analysis
python main.py analyze-dialux --input report.pdf

# Start web interface
python main.py web
```

### Advanced Options

```bash
# Specify output directory
python main.py analyze-dialux-fast --input report.pdf --output ./results

# Enable verbose logging
python main.py analyze-dialux-fast --input report.pdf --verbose

# Set OpenAI API key via environment variable
export OPENAI_API_KEY="sk-..."
python main.py analyze-dialux-enhanced --input report.pdf
```

## 📊 Analysis Methods

### ⚡ Fast Analysis

**Purpose**: Quick analysis with focus on essential data extraction

**Features**:
- Regex-based numerical extraction
- Area calculation with multiple patterns
- Company name extraction (with optional OpenAI enhancement)
- Basic compliance checking
- Processing time: 2-5 seconds

**Best for**:
- Quick project assessments
- Area verification
- Basic compliance checking
- Batch processing

### 🤖 Enhanced Analysis

**Purpose**: Comprehensive analysis with AI-powered extraction

**Features**:
- OpenAI GPT-4 powered extraction
- Detailed company information
- Comprehensive metadata extraction
- Full standards compliance checking
- Processing time: 10-30 seconds

**Best for**:
- Complete project analysis
- Detailed reports
- Company information extraction
- Professional documentation

### 🔍 Standard Analysis

**Purpose**: Traditional multi-method extraction with maximum compatibility

**Features**:
- Multiple PDF extraction methods
- Advanced table extraction
- Comprehensive error handling
- Full feature set
- Processing time: 30-60 seconds

**Best for**:
- Complex PDF formats
- Maximum compatibility
- Research and development
- Detailed technical analysis

## 📋 Standards Compliance

### Supported Standards

#### EN 12464-1:2021 - Light and lighting - Lighting of work places
- **Illuminance requirements** for different room types
- **Uniformity ratios** for visual comfort
- **UGR limits** for glare control
- **Power density limits** for energy efficiency
- **Color temperature** and CRI requirements

#### BREEAM - Building Research Establishment Environmental Assessment Method
- **Energy efficiency** requirements
- **Environmental impact** assessment
- **Sustainability** criteria
- **Performance standards**

### Compliance Checking

The system performs comprehensive compliance checking:

1. **Parameter Extraction**: Extracts lighting parameters from PDFs
2. **Standards Mapping**: Maps room types to appropriate standards
3. **Compliance Verification**: Compares actual vs required values
4. **Deviation Calculation**: Calculates exact differences
5. **Compliance Scoring**: Provides percentage compliance rates

### Room Type Mapping

- **Office**: General office spaces
- **Meeting Room**: Conference and meeting areas
- **Corridor**: Hallways and passageways
- **Storage**: Warehouses and storage areas
- **Industrial**: Manufacturing and production areas
- **Retail**: Commercial and retail spaces
- **Educational**: Schools and classrooms
- **Healthcare**: Hospitals and medical facilities
- **Residential**: Homes and apartments
- **Outdoor**: Exterior and outdoor areas

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# OpenAI API Key (for enhanced analysis)
OPENAI_API_KEY=sk-your-api-key-here

# Logging level
LOG_LEVEL=INFO

# Output directory
OUTPUT_DIR=./outputs

# Standards directory
STANDARDS_DIR=./data/standards
```

### Configuration Files

The system uses `src/core/config.py` for configuration:

```python
# Main configuration
config = AppConfig(
    project_root=Path(__file__).parent.parent.parent,
    data_dir=Path("data"),
    logs_dir=Path("logs"),
    outputs_dir=Path("outputs"),
    log_level="INFO"
)

# Dialux analysis configuration
dialux_config = DialuxConfig(
    extract_illuminance=True,
    extract_uniformity=True,
    extract_ugr=True,
    extract_power_density=True,
    extract_color_properties=True,
    min_room_area=1.0,
    max_room_area=10000.0,
    check_illuminance_compliance=True,
    check_uniformity_compliance=True,
    check_glare_compliance=True,
    check_power_compliance=True
)
```

## 📚 API Reference

### Core Classes

#### `PDFExtractor`
```python
from src.extractors.pdf_extractor import PDFExtractor

extractor = PDFExtractor()
result = extractor.extract_text_from_pdf("report.pdf")
```

#### `FastDialuxAnalyzer`
```python
from src.analyzers.fast_dialux_analyzer import FastDialuxAnalyzer

analyzer = FastDialuxAnalyzer(api_key="sk-...")
result = analyzer.analyze_dialux_report("report.pdf")
```

#### `StandardsProcessor`
```python
from src.standards.standards_processor import StandardsProcessor

processor = StandardsProcessor()
standards = processor.get_standards_for_room_type(RoomType.OFFICE)
```

### Data Classes

#### `FastRoomAnalysis`
```python
@dataclass
class FastRoomAnalysis:
    room_name: str
    room_type: str
    area: float
    illuminance_avg: Optional[float] = None
    uniformity: Optional[float] = None
    ugr: Optional[float] = None
    power_density: Optional[float] = None
    compliance_results: List[ComplianceResult] = None
```

#### `ComplianceResult`
```python
@dataclass
class ComplianceResult:
    standard: str
    parameter: str
    actual_value: float
    required_value: float
    unit: str
    is_compliant: bool
    deviation: float
```

## 📁 Output Formats

### JSON Export
```json
{
  "report": {
    "project_name": "Office Building Project",
    "project_company": "ABC Construction",
    "luminaire_manufacturer": "Philips",
    "total_rooms": 5,
    "total_area": 250.0,
    "overall_compliance_rate": 0.85
  },
  "rooms": [
    {
      "room_name": "Office 1",
      "room_type": "office",
      "area": 50.0,
      "illuminance_avg": 520.0,
      "uniformity": 0.65,
      "ugr": 18.5,
      "compliance_results": [...]
    }
  ],
  "recommendations": [...],
  "critical_issues": [...]
}
```

### CSV Export
```csv
Room Name,Room Type,Area (m²),Illuminance (lux),Uniformity,UGR,Power Density (W/m²),Compliance Rate
Office 1,office,50.0,520.0,0.65,18.5,8.5,85%
Office 2,office,45.0,480.0,0.62,19.2,9.1,78%
```

### Excel Export
- **Summary Sheet**: Project overview and statistics
- **Room Analysis**: Detailed room-by-room data
- **Compliance**: Standards comparison tables
- **Recommendations**: Categorized recommendations
- **Critical Issues**: Priority issues requiring attention

## 🔧 Troubleshooting

### Common Issues

#### 1. Installation Errors

**Error**: `ERROR: Could not find a version that satisfies the requirement pdf2image>=3.1.0`

**Solution**: Use the corrected requirements file:
```bash
pip install -r requirements.txt
```

#### 2. Java Not Found

**Error**: `JavaNotFoundError: `java` command is not found`

**Solution**: Install Java 8+ and add to PATH:
```bash
# Windows: Download from Oracle or use Chocolatey
choco install openjdk

# macOS: Use Homebrew
brew install openjdk@11

# Linux: Use package manager
sudo apt-get install openjdk-11-jdk
```

#### 3. Tesseract OCR Not Found

**Error**: `TesseractNotFoundError: tesseract is not installed`

**Solution**: Install Tesseract OCR:
```bash
# Windows: Download from GitHub releases
# macOS: Use Homebrew
brew install tesseract

# Linux: Use package manager
sudo apt-get install tesseract-ocr
```

#### 4. OpenAI API Key Issues

**Error**: `OpenAI API key is required for enhanced analysis`

**Solution**: Set your API key:
```bash
# Environment variable
export OPENAI_API_KEY="sk-your-key-here"

# Or pass as parameter
python main.py analyze-dialux-enhanced --api-key "sk-your-key-here"
```

#### 5. Area Extraction Issues

**Issue**: Area always shows as 1.0 m²

**Solution**: 
- Use Fast Analysis method for better area extraction
- Check if your PDF uses different area notation
- Try Enhanced Analysis with OpenAI for better extraction

#### 6. Import Errors

**Error**: `ImportError: attempted relative import with no known parent package`

**Solution**: Run from the correct directory:
```bash
cd unified_lighting_analyzer
python main.py [command]
```

### Performance Optimization

#### For Large PDFs
- Use Fast Analysis for quick results
- Enable verbose logging to monitor progress
- Consider splitting large PDFs into smaller sections

#### For Better Accuracy
- Use Enhanced Analysis with OpenAI API key
- Ensure good PDF quality (not heavily scanned)
- Verify table structure in source PDF

#### For Batch Processing
- Use command line interface
- Set up proper output directories
- Monitor system resources during processing

## 🤝 Contributing

We welcome contributions to improve the Unified Lighting Analyzer!

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/unified-lighting-analyzer.git
cd unified-lighting-analyzer

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run linting
black src/
flake8 src/
mypy src/
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Add docstrings for all classes and methods
- Write tests for new features
- Update documentation for changes

### Areas for Contribution

- **New extraction methods** for different PDF formats
- **Additional standards** support
- **Enhanced AI models** for better extraction
- **Performance optimizations**
- **UI/UX improvements**
- **Documentation** improvements
- **Test coverage** expansion

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### MIT License

```
MIT License

Copyright (c) 2024 Short Circuit Company

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 📞 Contact

### Short Circuit Company

- **Email**: [Scc@shortcircuitcompany.com](mailto:Scc@shortcircuitcompany.com)
- **Website**: [www.shortcircuitcompany.com](https://www.shortcircuitcompany.com)
- **GitHub**: [@shortcircuitcompany](https://github.com/shortcircuitcompany)

### Project Maintainers

- **Lead Developer**: AI Development Team
- **Technical Support**: [Scc@shortcircuitcompany.com](mailto:Scc@shortcircuitcompany.com)
- **Feature Requests**: [GitHub Issues](https://github.com/your-username/unified-lighting-analyzer/issues)

### Support

For technical support, feature requests, or bug reports:

1. **Check the documentation** and troubleshooting section
2. **Search existing issues** on GitHub
3. **Create a new issue** with detailed information
4. **Contact us directly** at [Scc@shortcircuitcompany.com](mailto:Scc@shortcircuitcompany.com)

---

**Made with ❤️ by [Short Circuit Company](https://www.shortcircuitcompany.com)**