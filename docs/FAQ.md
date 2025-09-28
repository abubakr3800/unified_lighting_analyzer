# Frequently Asked Questions (FAQ)

## 📋 Table of Contents

1. [General Questions](#general-questions)
2. [Installation Questions](#installation-questions)
3. [Usage Questions](#usage-questions)
4. [Technical Questions](#technical-questions)
5. [Troubleshooting Questions](#troubleshooting-questions)
6. [Performance Questions](#performance-questions)
7. [Security Questions](#security-questions)

## 🤔 General Questions

### What is the Unified Lighting Analyzer?

The Unified Lighting Analyzer is a comprehensive AI-powered system for analyzing lighting documents, standards compliance, and Dialux reports. It combines multiple extraction methods, standards compliance checking, and detailed analysis reports for lighting professionals.

### Who developed this project?

This project was developed by **Short Circuit Company** (Scc@shortcircuitcompany.com). It combines the best features from multiple lighting analysis projects into a single, unified solution.

### What types of files can the system analyze?

The system is designed to analyze **PDF files**, specifically:
- Dialux report PDFs
- Lighting standards documents
- General lighting analysis reports
- Technical documentation with tables and data

### What lighting standards are supported?

Currently supported standards:
- **EN 12464-1:2021** - Light and lighting - Lighting of work places
- **BREEAM** - Building Research Establishment Environmental Assessment Method

Planned additions:
- IES (Illuminating Engineering Society) standards
- ASHRAE (American Society of Heating, Refrigerating and Air-Conditioning Engineers) standards
- Custom standards support

### Is the software free to use?

Yes, the Unified Lighting Analyzer is **open source** and available under the **MIT License**. You can use, modify, and distribute it freely. However, some features (like Enhanced Analysis) require an OpenAI API key, which has its own costs.

### What are the main features?

Key features include:
- **Multi-method PDF extraction** with fallback strategies
- **Advanced table extraction** with quality analysis
- **Intelligent Dialux report analysis** with AI-powered extraction
- **Standards compliance checking** against multiple standards
- **Comprehensive recommendations** with priority levels
- **Interactive web interface** with real-time results
- **Multiple export formats** for integration with other tools

## 🛠️ Installation Questions

### What are the system requirements?

**Minimum Requirements:**
- Python 3.8+
- 4 GB RAM
- 2 GB free storage
- Java 8+ (for table extraction)
- Tesseract OCR (for OCR functionality)

**Recommended Requirements:**
- Python 3.9+
- 8 GB RAM
- 5 GB free storage
- Multi-core processor

### How do I install the software?

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/unified-lighting-analyzer.git
   cd unified-lighting-analyzer
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install system dependencies** (Java, Tesseract OCR)

4. **Verify installation**:
   ```bash
   python main.py --help
   ```

For detailed instructions, see the [Installation Guide](INSTALLATION.md).

### Do I need to install Java?

Yes, **Java 8+** is required for the Camelot table extraction functionality. You can install it using:

- **Windows**: `choco install openjdk` or download from Oracle
- **macOS**: `brew install openjdk@11`
- **Linux**: `sudo apt install openjdk-11-jdk`

### Do I need to install Tesseract OCR?

Yes, **Tesseract OCR** is required for OCR functionality. Install it using:

- **Windows**: `choco install tesseract` or download from GitHub
- **macOS**: `brew install tesseract`
- **Linux**: `sudo apt install tesseract-ocr`

### Can I use Docker instead of local installation?

Yes, Docker installation is supported as an alternative:

```bash
# Build Docker image
docker build -t unified-lighting-analyzer .

# Run container
docker run -p 8501:8501 -v $(pwd)/data:/app/data unified-lighting-analyzer
```

### What if I get installation errors?

Common solutions:
- **Update pip**: `pip install --upgrade pip`
- **Use virtual environment**: `python -m venv venv`
- **Install minimal requirements**: `pip install -r requirements-minimal.txt`
- **Check system dependencies**: Ensure Java and Tesseract are installed

For detailed troubleshooting, see the [Installation Guide](INSTALLATION.md).

## 💻 Usage Questions

### How do I start using the software?

1. **Start the web interface**:
   ```bash
   streamlit run web_app.py
   ```

2. **Open your browser** to `http://localhost:8501`

3. **Upload a PDF** and choose analysis method

4. **Review the comprehensive results**

### What analysis methods are available?

Three analysis methods are available:

- **⚡ Fast Analysis** (Recommended): Quick extraction with regex patterns (2-5 seconds)
- **🤖 Enhanced Analysis**: OpenAI-powered comprehensive extraction (10-30 seconds)
- **🔍 Standard Analysis**: Traditional multi-method approach (30-60 seconds)

### Do I need an OpenAI API key?

- **Fast Analysis**: API key is optional (for enhanced company extraction)
- **Enhanced Analysis**: API key is required
- **Standard Analysis**: API key is not required

### How do I get an OpenAI API key?

1. **Sign up** at [OpenAI Platform](https://platform.openai.com/)
2. **Create an API key** in your account settings
3. **Add credits** to your account
4. **Use the key** in the application

### What information does the system extract?

The system extracts:
- **Project information**: Name, company, dates
- **Company details**: Project company, luminaire manufacturer, driver circuit company
- **Room data**: Area, illuminance, uniformity, UGR, power density
- **Lighting parameters**: Color temperature, CRI, spacing, mounting height
- **Compliance data**: Standards comparison and compliance rates

### How accurate is the extraction?

Accuracy depends on the analysis method:
- **Fast Analysis**: High accuracy for numerical data, moderate for text
- **Enhanced Analysis**: Very high accuracy with AI extraction
- **Standard Analysis**: High accuracy with multiple extraction methods

The system provides a **data quality score** to indicate extraction confidence.

### Can I analyze multiple files at once?

Yes, you can use the command line interface for batch processing:

```bash
# Process multiple files
for file in *.pdf; do
    python main.py analyze-dialux-fast --input "$file" --output "./results/$file"
done
```

## 🔧 Technical Questions

### What programming language is used?

The system is built in **Python 3.8+** with the following key libraries:
- **Streamlit** for the web interface
- **pdfplumber, PyMuPDF, pdfminer** for PDF processing
- **Camelot** for table extraction
- **OpenAI** for AI-powered extraction
- **pandas, numpy** for data processing

### How does the extraction work?

The system uses a **multi-method approach** with fallback strategies:

1. **PDF Text Extraction**: pdfplumber → PyMuPDF → pdfminer → OCR
2. **Table Extraction**: Camelot → pdfplumber → OCR with quality filtering
3. **Data Extraction**: Regex patterns → AI extraction (optional)
4. **Standards Comparison**: Pre-defined standards database

### What is the architecture?

The system follows a **modular architecture**:
- **Extractors**: PDF and table extraction modules
- **Analyzers**: Analysis and processing modules
- **Standards**: Standards management and compliance checking
- **Web Interface**: Streamlit-based user interface
- **CLI**: Command-line interface for batch processing

### Can I extend the system?

Yes, the system is designed for extensibility:
- **New extraction methods** can be added
- **Additional standards** can be integrated
- **Custom analyzers** can be developed
- **API endpoints** can be added

See the [Contributing Guide](CONTRIBUTING.md) for details.

### How does standards compliance work?

The system:
1. **Extracts lighting parameters** from PDFs
2. **Maps room types** to appropriate standards
3. **Compares actual vs required values**
4. **Calculates compliance rates** and deviations
5. **Generates recommendations** for improvements

### What data formats are supported for export?

Supported export formats:
- **JSON**: Complete analysis data
- **CSV**: Room-by-room data
- **Excel**: Multiple sheets with comprehensive data
- **PDF**: Report generation (planned)

## 🔍 Troubleshooting Questions

### Why is the area always showing as 1.0 m²?

This indicates area extraction failed. Solutions:
- **Use Fast Analysis** method for better area extraction
- **Check PDF format** - ensure area values are clearly visible
- **Try Enhanced Analysis** with OpenAI for better extraction
- **Verify PDF quality** - avoid heavily scanned documents

### Why is the processing taking too long?

Processing time depends on the method:
- **Fast Analysis**: 2-5 seconds
- **Enhanced Analysis**: 10-30 seconds
- **Standard Analysis**: 30-60 seconds

If it's taking longer:
- **Check system resources** (CPU, memory)
- **Use Fast Analysis** for quicker results
- **Try smaller PDF files**
- **Check for system bottlenecks**

### Why am I getting import errors?

Common causes and solutions:
- **Wrong directory**: Run from the project root directory
- **Missing dependencies**: Install requirements.txt
- **Python path issues**: Use virtual environment
- **Version conflicts**: Update pip and packages

### Why is the web interface not starting?

Common solutions:
- **Check port availability**: Ensure port 8501 is free
- **Install Streamlit**: `pip install streamlit`
- **Check Python path**: Run from correct directory
- **Update dependencies**: `pip install --upgrade streamlit`

### Why are company names not being extracted?

Solutions:
- **Use Enhanced Analysis** with OpenAI API key
- **Check PDF quality** - ensure text is selectable
- **Try different analysis methods**
- **Verify company info is visible** in the PDF

### Why am I getting compliance errors?

Common causes:
- **Room type classification** may be incorrect
- **Standards requirements** may not match your region
- **Extracted values** may need manual verification
- **PDF format** may not be compatible

## ⚡ Performance Questions

### How can I improve processing speed?

Optimization tips:
- **Use Fast Analysis** for quick results
- **Process smaller files** when possible
- **Use SSD storage** for better I/O performance
- **Increase system RAM** for large files
- **Use command line** for batch processing

### What file sizes are supported?

Recommended limits:
- **Maximum file size**: 50 MB
- **Optimal file size**: 5-20 MB
- **Minimum file size**: 100 KB

For larger files:
- **Split into smaller sections**
- **Use command line processing**
- **Increase system resources**

### How much memory does the system use?

Memory usage depends on:
- **File size**: Larger files use more memory
- **Analysis method**: Enhanced Analysis uses more memory
- **System configuration**: Available RAM affects performance

Typical usage:
- **Fast Analysis**: 100-500 MB
- **Enhanced Analysis**: 500 MB - 2 GB
- **Standard Analysis**: 200 MB - 1 GB

### Can I run multiple analyses simultaneously?

Yes, but consider:
- **System resources**: Each analysis uses CPU and memory
- **API limits**: OpenAI API has rate limits
- **File conflicts**: Avoid processing the same file simultaneously

For batch processing, use the command line interface.

## 🔒 Security Questions

### Is my data secure?

Security measures:
- **Local processing**: Data is processed locally by default
- **No data storage**: Files are not permanently stored
- **Secure API keys**: Keys are handled securely
- **Input validation**: All inputs are validated

### What happens to my uploaded files?

File handling:
- **Temporary storage**: Files are stored temporarily during processing
- **Automatic cleanup**: Files are deleted after processing
- **No permanent storage**: Files are not saved permanently
- **Local processing**: Processing happens on your machine

### Are API keys secure?

API key security:
- **Environment variables**: Keys are stored securely
- **No logging**: Keys are not logged or exposed
- **Session-based**: Keys are only used during the session
- **User control**: You control when and how keys are used

### Can I use the system offline?

Offline capabilities:
- **Fast Analysis**: Works completely offline
- **Standard Analysis**: Works offline (except for some dependencies)
- **Enhanced Analysis**: Requires internet for OpenAI API

### What about privacy?

Privacy considerations:
- **Local processing**: Data stays on your machine
- **No data sharing**: Data is not shared with third parties
- **User control**: You control what data is processed
- **Transparent processing**: You can see what data is extracted

---

## 📞 Getting Help

### Where can I get more help?

- **Documentation**: Check the [User Guide](USER_GUIDE.md) and [API Reference](API_REFERENCE.md)
- **GitHub Issues**: Search existing issues or create a new one
- **Email Support**: Contact [Scc@shortcircuitcompany.com](mailto:Scc@shortcircuitcompany.com)
- **Community**: Join discussions on GitHub

### How do I report a bug?

1. **Check existing issues** on GitHub
2. **Create a new issue** with detailed information:
   - System information (OS, Python version)
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages and logs
   - Sample files (if applicable)

### How do I request a feature?

1. **Check existing feature requests**
2. **Create a new issue** with:
   - Clear description of the feature
   - Use case and benefits
   - Implementation suggestions (if any)
   - Priority level

### Can I contribute to the project?

Yes! We welcome contributions:
- **Code contributions**: Bug fixes, new features, improvements
- **Documentation**: Guides, examples, translations
- **Testing**: Bug reports, test cases, quality assurance
- **Feedback**: User experience, feature requests

See the [Contributing Guide](CONTRIBUTING.md) for details.

---

**For additional questions not covered here, please contact [Short Circuit Company](mailto:Scc@shortcircuitcompany.com) or create an issue on GitHub.**
