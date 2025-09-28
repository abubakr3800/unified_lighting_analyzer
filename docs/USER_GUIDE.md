# User Guide - Unified Lighting Analyzer

## 📖 Table of Contents

1. [Getting Started](#getting-started)
2. [Web Interface Guide](#web-interface-guide)
3. [Command Line Guide](#command-line-guide)
4. [Understanding Results](#understanding-results)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Usage](#advanced-usage)

## 🚀 Getting Started

### First Time Setup

1. **Install the software** following the [Installation Guide](INSTALLATION.md)
2. **Verify installation** by running: `python main.py --help`
3. **Start the web interface**: `streamlit run web_app.py`
4. **Open your browser** to `http://localhost:8501`

### Quick Test

1. **Download a sample Dialux report** (PDF format)
2. **Upload it** to the web interface
3. **Choose "Fast Analysis"** for quick results
4. **Review the comprehensive report** generated

## 🌐 Web Interface Guide

### Navigation Overview

The web interface has five main sections:

- **🏠 Home**: Project overview and getting started information
- **📄 PDF Extraction**: Basic PDF text and table extraction
- **📊 Table Analysis**: Advanced table extraction and analysis
- **📋 Standards Processing**: Lighting standards management
- **🏢 Dialux Analysis**: Comprehensive Dialux report analysis

### Dialux Analysis Page

This is the main feature of the application. Here's how to use it:

#### Step 1: Choose Analysis Method

**⚡ Fast Analysis (Recommended)**
- **Best for**: Quick assessments, area verification, basic compliance
- **Speed**: 2-5 seconds
- **Features**: Regex-based extraction, company info, basic compliance
- **API Key**: Optional (for enhanced company extraction)

**🤖 Enhanced Analysis**
- **Best for**: Complete project analysis, detailed reports
- **Speed**: 10-30 seconds
- **Features**: AI-powered extraction, comprehensive metadata
- **API Key**: Required (OpenAI API key)

**🔍 Standard Analysis**
- **Best for**: Complex PDFs, maximum compatibility
- **Speed**: 30-60 seconds
- **Features**: Multi-method extraction, comprehensive analysis
- **API Key**: Not required

#### Step 2: Set API Key (if needed)

For Enhanced Analysis, you'll need an OpenAI API key:

1. **Get an API key** from [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Enter it** in the "OpenAI API Key" field
3. **Keep it secure** - it's only used for this session

#### Step 3: Upload PDF

1. **Click "Choose a Dialux report PDF"**
2. **Select your PDF file** from your computer
3. **Wait for upload** to complete
4. **Click "Analyze"** to start processing

#### Step 4: Review Results

The analysis will show:

1. **Processing time** and success message
2. **Project overview** with key metrics
3. **Detailed room analysis** with expandable sections
4. **Comprehensive standards comparison** with tables
5. **Categorized recommendations** with priority levels
6. **Critical issues** requiring immediate attention
7. **Export options** for reports

### Understanding the Results

#### Project Overview Section

- **Project Name**: Extracted from the PDF
- **Total Rooms**: Number of rooms analyzed
- **Total Area**: Sum of all room areas
- **Overall Compliance**: Percentage of parameters meeting standards
- **Data Quality Score**: Confidence in the extraction accuracy

#### Company Information

- **Project Company**: Client or project owner
- **Luminaire Manufacturer**: Lighting fixture manufacturer
- **Driver Circuit Company**: Electronic driver manufacturer
- **Consultant**: Lighting design consultant (if available)
- **Installer**: Installation company (if available)

#### Room Analysis

Each room shows:

**Basic Metrics**:
- **Area**: Room area in square meters
- **Average Illuminance**: Mean illuminance level
- **Uniformity**: Light distribution uniformity ratio
- **UGR**: Unified Glare Rating
- **Power Density**: Watts per square meter

**Detailed Parameters**:
- **Min/Max Illuminance**: Range of illuminance values
- **Color Temperature**: Light color in Kelvin
- **CRI**: Color Rendering Index
- **Luminaire Spacing**: Distance between fixtures
- **Mounting Height**: Height of luminaires above floor

#### Standards Comparison

For each standard (EN 12464-1, BREEAM):

- **Parameter-by-parameter comparison** in detailed tables
- **Compliance status** with visual indicators (✅/❌)
- **Actual vs Required values** with exact differences
- **Deviation calculations** showing how far off each parameter is
- **Compliance percentages** with color-coded status

#### Recommendations

**Categorized by Type**:
- **🔆 Illuminance**: Light level improvements
- **📐 Uniformity**: Light distribution improvements
- **👁️ Glare Control**: Glare reduction measures
- **⚡ Power Efficiency**: Energy optimization
- **📋 General**: Project-wide recommendations
- **🔧 Maintenance**: Long-term maintenance planning
- **🤖 Smart Lighting**: Advanced control systems

**Priority Levels**:
- **🚨 CRITICAL**: Immediate action required
- **⚠️ HIGH PRIORITY**: Important improvements needed
- **📋 MODERATE**: Minor adjustments recommended
- **💡 ENERGY SAVING**: Efficiency optimizations

#### Critical Issues

Issues requiring immediate attention:

- **🚨 SEVERE**: Safety and productivity risks
- **🚨 CRITICAL**: Significant compliance problems
- **⚠️ HIGH PRIORITY**: Important improvements needed
- **Project-Level Issues**: Overall compliance assessment
- **Data Quality Issues**: Analysis confidence warnings

## 💻 Command Line Guide

### Basic Commands

```bash
# Show help
python main.py --help

# Fast analysis (recommended)
python main.py analyze-dialux-fast --input report.pdf

# Enhanced analysis with OpenAI
python main.py analyze-dialux-enhanced --input report.pdf --api-key sk-...

# Standard analysis
python main.py analyze-dialux --input report.pdf

# Start web interface
python main.py web
```

### Command Options

#### Input Options
- `--input, -i`: Path to input PDF file (required)
- `--output, -o`: Output directory (optional, default: ./outputs)

#### Analysis Options
- `--api-key`: OpenAI API key for enhanced analysis
- `--verbose, -v`: Enable detailed logging output

#### Examples

```bash
# Basic fast analysis
python main.py analyze-dialux-fast --input "C:\Reports\office_report.pdf"

# Enhanced analysis with custom output
python main.py analyze-dialux-enhanced --input report.pdf --api-key sk-... --output ./results

# Verbose standard analysis
python main.py analyze-dialux --input report.pdf --verbose
```

### Output Files

The system generates several output files:

- **`analysis_report.json`**: Complete analysis results in JSON format
- **`room_analysis.csv`**: Room-by-room data in CSV format
- **`compliance_summary.xlsx`**: Excel workbook with multiple sheets
- **`recommendations.txt`**: Text file with all recommendations
- **`critical_issues.txt`**: Text file with critical issues

## 📊 Understanding Results

### Compliance Rates

**Excellent (90-100%)**: All or nearly all parameters meet standards
**Good (80-89%)**: Most parameters meet standards, minor improvements needed
**Fair (60-79%)**: Some parameters need improvement
**Poor (40-59%)**: Significant improvements required
**Critical (<40%)**: Major lighting system redesign needed

### Parameter Interpretations

#### Illuminance (Lux)
- **500+ lux**: Excellent for office work
- **300-500 lux**: Good for general tasks
- **200-300 lux**: Adequate for basic tasks
- **<200 lux**: Insufficient for most work

#### Uniformity (Ratio)
- **0.7+**: Excellent light distribution
- **0.6-0.7**: Good distribution
- **0.4-0.6**: Fair distribution
- **<0.4**: Poor distribution, potential eye strain

#### UGR (Unified Glare Rating)
- **<16**: Excellent, no glare issues
- **16-19**: Good, minimal glare
- **19-22**: Acceptable, some glare
- **22-25**: Noticeable glare
- **>25**: Unacceptable glare levels

#### Power Density (W/m²)
- **<8 W/m²**: Excellent energy efficiency
- **8-12 W/m²**: Good efficiency
- **12-15 W/m²**: Acceptable efficiency
- **>15 W/m²**: Poor efficiency, consider LED retrofit

### Data Quality Scores

- **90-100%**: Very high confidence in extraction
- **80-89%**: High confidence, minor uncertainties
- **70-79%**: Good confidence, some parameters may need verification
- **60-69%**: Moderate confidence, manual verification recommended
- **<60%**: Low confidence, significant manual review needed

## 🎯 Best Practices

### PDF Preparation

1. **Use high-quality PDFs**: Avoid heavily scanned documents
2. **Ensure text is selectable**: Use PDFs with embedded text, not just images
3. **Check table structure**: Ensure tables are properly formatted
4. **Include all pages**: Make sure all relevant pages are included

### Analysis Selection

1. **Start with Fast Analysis**: For quick initial assessment
2. **Use Enhanced Analysis**: For comprehensive reports and company info
3. **Use Standard Analysis**: For complex or problematic PDFs
4. **Compare results**: Try different methods for validation

### Results Interpretation

1. **Check data quality score**: Ensure extraction confidence is adequate
2. **Review critical issues first**: Address the most important problems
3. **Prioritize recommendations**: Focus on critical and high-priority items
4. **Verify area calculations**: Ensure room areas are correctly extracted
5. **Cross-reference standards**: Check against multiple standards when available

### Export and Documentation

1. **Export multiple formats**: Use JSON for data, Excel for presentations
2. **Save recommendations**: Keep track of all improvement suggestions
3. **Document critical issues**: Create action plans for immediate problems
4. **Archive results**: Keep analysis results for future reference

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Area Shows as 1.0 m²
**Problem**: Area extraction failed
**Solutions**:
- Try Fast Analysis method
- Check if PDF uses different area notation (sqm, square meters, etc.)
- Use Enhanced Analysis with OpenAI for better extraction
- Manually verify area values in source PDF

#### Low Data Quality Score
**Problem**: Extraction confidence is low
**Solutions**:
- Use Enhanced Analysis with OpenAI API key
- Check PDF quality and text selectability
- Try Standard Analysis for better compatibility
- Manually verify extracted values

#### Missing Company Information
**Problem**: Company names not extracted
**Solutions**:
- Use Enhanced Analysis with OpenAI API key
- Check if company info is clearly visible in PDF
- Try different analysis methods
- Manually add company information to results

#### Compliance Issues
**Problem**: Many parameters showing non-compliant
**Solutions**:
- Verify room type classification is correct
- Check if standards requirements are appropriate
- Review actual vs required values carefully
- Consider if different standards apply

#### Slow Processing
**Problem**: Analysis taking too long
**Solutions**:
- Use Fast Analysis for quicker results
- Check system resources (CPU, memory)
- Try smaller PDF files
- Use command line for batch processing

### Getting Help

1. **Check the documentation**: Review this guide and README
2. **Search existing issues**: Look for similar problems on GitHub
3. **Create a new issue**: Provide detailed information about the problem
4. **Contact support**: Email [Scc@shortcircuitcompany.com](mailto:Scc@shortcircuitcompany.com)

## 🚀 Advanced Usage

### Batch Processing

For multiple PDFs:

```bash
# Process multiple files
for file in *.pdf; do
    python main.py analyze-dialux-fast --input "$file" --output "./results/$file"
done
```

### Custom Configuration

Create a custom configuration file:

```python
# custom_config.py
from src.core.config import AppConfig, DialuxConfig

custom_config = AppConfig(
    outputs_dir=Path("./custom_outputs"),
    log_level="DEBUG"
)

custom_dialux_config = DialuxConfig(
    min_room_area=5.0,  # Custom minimum area
    max_room_area=5000.0,  # Custom maximum area
    check_illuminance_compliance=True,
    check_uniformity_compliance=True
)
```

### API Integration

Use the analyzer in your own applications:

```python
from src.analyzers.fast_dialux_analyzer import FastDialuxAnalyzer

# Initialize analyzer
analyzer = FastDialuxAnalyzer(api_key="your-api-key")

# Analyze report
result = analyzer.analyze_dialux_report("report.pdf")

# Access results
print(f"Project: {result.report.project_name}")
print(f"Compliance: {result.report.overall_compliance_rate:.1%}")
print(f"Recommendations: {len(result.recommendations)}")
```

### Custom Standards

Add your own lighting standards:

```python
# Add to standards database
custom_standard = {
    "name": "Custom Standard",
    "version": "2024",
    "requirements": {
        "office": {
            "illuminance_min": 400,
            "uniformity_min": 0.5,
            "ugr_max": 20,
            "power_density_max": 10
        }
    }
}
```

---

**For more information, visit our [GitHub repository](https://github.com/your-username/unified-lighting-analyzer) or contact [Short Circuit Company](mailto:Scc@shortcircuitcompany.com).**
