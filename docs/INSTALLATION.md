# Installation Guide - Unified Lighting Analyzer

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Methods](#installation-methods)
3. [Platform-Specific Instructions](#platform-specific-instructions)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)
6. [Uninstallation](#uninstallation)

## 💻 System Requirements

### Minimum Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **RAM**: 4 GB minimum, 8 GB recommended
- **Storage**: 2 GB free space
- **Internet**: Required for OpenAI API (Enhanced Analysis)

### Recommended Requirements

- **Operating System**: Windows 11, macOS 12+, or Linux (Ubuntu 20.04+)
- **Python**: 3.9 or higher
- **RAM**: 8 GB or more
- **Storage**: 5 GB free space
- **CPU**: Multi-core processor (4+ cores recommended)

### Required System Dependencies

- **Java 8+**: Required for Camelot table extraction
- **Tesseract OCR**: Required for OCR functionality
- **Git**: Required for cloning the repository

## 🚀 Installation Methods

### Method 1: Quick Installation (Recommended)

#### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/unified-lighting-analyzer.git
cd unified-lighting-analyzer
```

#### Step 2: Install Python Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# OR for minimal installation (core features only)
pip install -r requirements-minimal.txt
```

#### Step 3: Install System Dependencies

Follow the platform-specific instructions below.

### Method 2: Development Installation

#### Step 1: Clone and Setup

```bash
git clone https://github.com/your-username/unified-lighting-analyzer.git
cd unified-lighting-analyzer

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

#### Step 2: Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .
```

## 🖥️ Platform-Specific Instructions

### Windows Installation

#### Prerequisites

1. **Install Python 3.8+**
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **Install Java 8+**
   ```bash
   # Using Chocolatey (recommended)
   choco install openjdk

   # OR download from Oracle
   # https://www.oracle.com/java/technologies/downloads/
   ```

3. **Install Tesseract OCR**
   ```bash
   # Using Chocolatey (recommended)
   choco install tesseract

   # OR download from GitHub
   # https://github.com/UB-Mannheim/tesseract/wiki
   # Add to PATH: C:\Program Files\Tesseract-OCR
   ```

#### Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/your-username/unified-lighting-analyzer.git
cd unified-lighting-analyzer

# 2. Install Python packages
pip install -r requirements.txt

# 3. Verify installation
python -c "import streamlit, pdfplumber, camelot; print('✅ Installation successful!')"
```

#### Windows-Specific Notes

- **Path Issues**: If you get "command not found" errors, ensure Python and Java are in your PATH
- **Antivirus**: Some antivirus software may flag the installation - add exceptions if needed
- **PowerShell**: Use PowerShell or Command Prompt as Administrator if needed

### macOS Installation

#### Prerequisites

1. **Install Homebrew** (if not already installed)
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python 3.8+**
   ```bash
   brew install python@3.9
   ```

3. **Install Java 8+**
   ```bash
   brew install openjdk@11
   ```

4. **Install Tesseract OCR**
   ```bash
   brew install tesseract
   ```

#### Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/your-username/unified-lighting-analyzer.git
cd unified-lighting-analyzer

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install Python packages
pip install -r requirements.txt

# 4. Verify installation
python -c "import streamlit, pdfplumber, camelot; print('✅ Installation successful!')"
```

#### macOS-Specific Notes

- **Permissions**: You may need to allow Python to run in System Preferences > Security & Privacy
- **Xcode**: Install Xcode Command Line Tools if prompted: `xcode-select --install`
- **M1 Macs**: All packages should work natively on Apple Silicon

### Linux Installation (Ubuntu/Debian)

#### Prerequisites

1. **Update package list**
   ```bash
   sudo apt update
   sudo apt upgrade
   ```

2. **Install Python 3.8+**
   ```bash
   sudo apt install python3 python3-pip python3-venv
   ```

3. **Install Java 8+**
   ```bash
   sudo apt install openjdk-11-jdk
   ```

4. **Install Tesseract OCR**
   ```bash
   sudo apt install tesseract-ocr
   ```

5. **Install additional dependencies**
   ```bash
   sudo apt install build-essential libpoppler-cpp-dev pkg-config
   ```

#### Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/your-username/unified-lighting-analyzer.git
cd unified-lighting-analyzer

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install Python packages
pip install -r requirements.txt

# 4. Verify installation
python -c "import streamlit, pdfplumber, camelot; print('✅ Installation successful!')"
```

#### Linux-Specific Notes

- **Dependencies**: Some packages may require additional system libraries
- **Permissions**: Use `sudo` only when necessary for system packages
- **Virtual Environment**: Always use a virtual environment to avoid conflicts

### Docker Installation (Alternative)

#### Prerequisites

- **Docker**: Install Docker Desktop or Docker Engine
- **Docker Compose**: Usually included with Docker Desktop

#### Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/your-username/unified-lighting-analyzer.git
cd unified-lighting-analyzer

# 2. Build Docker image
docker build -t unified-lighting-analyzer .

# 3. Run container
docker run -p 8501:8501 -v $(pwd)/data:/app/data unified-lighting-analyzer
```

#### Docker Notes

- **Data Persistence**: Mount volumes for data persistence
- **Port Mapping**: Map port 8501 for web interface access
- **Resource Limits**: Set appropriate memory and CPU limits

## ✅ Verification

### Basic Verification

```bash
# Test Python installation
python --version
# Should show Python 3.8 or higher

# Test Java installation
java -version
# Should show Java 8 or higher

# Test Tesseract installation
tesseract --version
# Should show Tesseract version

# Test Python packages
python -c "import streamlit, pdfplumber, camelot, opencv-python; print('✅ All packages imported successfully!')"
```

### Application Verification

```bash
# Test command line interface
python main.py --help
# Should show help message with available commands

# Test web interface
streamlit run web_app.py
# Should start web server on http://localhost:8501
```

### Full System Test

```bash
# Run comprehensive test
python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('src')))

try:
    from core.config import config
    from extractors.pdf_extractor import PDFExtractor
    from analyzers.fast_dialux_analyzer import FastDialuxAnalyzer
    print('✅ All modules imported successfully!')
    print('✅ Configuration loaded successfully!')
    print('✅ System ready for use!')
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
"
```

## 🔧 Troubleshooting

### Common Installation Issues

#### 1. Python Version Issues

**Error**: `Python 3.8+ is required`

**Solution**:
```bash
# Check current version
python --version

# Install newer Python version
# Windows: Download from python.org
# macOS: brew install python@3.9
# Linux: sudo apt install python3.9
```

#### 2. Java Not Found

**Error**: `JavaNotFoundError: java command is not found`

**Solution**:
```bash
# Windows
choco install openjdk
# OR download from Oracle and add to PATH

# macOS
brew install openjdk@11

# Linux
sudo apt install openjdk-11-jdk
```

#### 3. Tesseract Not Found

**Error**: `TesseractNotFoundError: tesseract is not installed`

**Solution**:
```bash
# Windows
choco install tesseract
# OR download from GitHub and add to PATH

# macOS
brew install tesseract

# Linux
sudo apt install tesseract-ocr
```

#### 4. Package Installation Failures

**Error**: `ERROR: Could not find a version that satisfies the requirement`

**Solution**:
```bash
# Update pip
pip install --upgrade pip

# Try minimal requirements
pip install -r requirements-minimal.txt

# Install packages individually
pip install streamlit pdfplumber camelot-py
```

#### 5. Permission Issues

**Error**: `Permission denied` or `Access denied`

**Solution**:
```bash
# Use virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate  # Windows

# Install with user flag
pip install --user -r requirements.txt
```

#### 6. Import Errors

**Error**: `ImportError: No module named 'module_name'`

**Solution**:
```bash
# Check if package is installed
pip list | grep module_name

# Reinstall package
pip uninstall module_name
pip install module_name

# Check Python path
python -c "import sys; print(sys.path)"
```

### Platform-Specific Issues

#### Windows Issues

**Issue**: `'streamlit' is not recognized as an internal or external command`

**Solution**:
```bash
# Add Python Scripts to PATH
# Add: C:\Users\YourName\AppData\Local\Programs\Python\Python39\Scripts

# Or use python -m
python -m streamlit run web_app.py
```

**Issue**: Antivirus blocking installation

**Solution**:
- Add Python installation directory to antivirus exceptions
- Temporarily disable real-time protection during installation
- Use Windows Defender exclusions

#### macOS Issues

**Issue**: `xcrun: error: invalid active developer path`

**Solution**:
```bash
# Install Xcode Command Line Tools
xcode-select --install
```

**Issue**: Permission denied for Python

**Solution**:
```bash
# Allow Python in System Preferences > Security & Privacy
# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
```

#### Linux Issues

**Issue**: `Package 'package-name' has no installation candidate`

**Solution**:
```bash
# Update package list
sudo apt update

# Install build tools
sudo apt install build-essential

# Install specific packages
sudo apt install python3-dev libffi-dev libssl-dev
```

**Issue**: `ImportError: libcairo.so.2: cannot open shared object file`

**Solution**:
```bash
# Install Cairo library
sudo apt install libcairo2-dev

# Install additional dependencies
sudo apt install libpango1.0-dev libgdk-pixbuf2.0-dev libffi-dev shared-mime-info
```

### Getting Help

If you encounter issues not covered here:

1. **Check the logs**: Look for error messages in the terminal output
2. **Search existing issues**: Check GitHub issues for similar problems
3. **Create a new issue**: Provide detailed information about your system and the error
4. **Contact support**: Email [Scc@shortcircuitcompany.com](mailto:Scc@shortcircuitcompany.com)

## 🗑️ Uninstallation

### Complete Removal

#### Windows

```bash
# Remove Python packages
pip uninstall -r requirements.txt -y

# Remove virtual environment
rmdir /s venv

# Remove project directory
rmdir /s unified-lighting-analyzer
```

#### macOS/Linux

```bash
# Deactivate virtual environment
deactivate

# Remove Python packages
pip uninstall -r requirements.txt -y

# Remove virtual environment
rm -rf venv

# Remove project directory
rm -rf unified-lighting-analyzer
```

### Partial Removal

```bash
# Remove only the project
rm -rf unified-lighting-analyzer

# Keep Python packages (if used by other projects)
# Keep system dependencies (Java, Tesseract)
```

### System Dependencies

**Note**: System dependencies (Java, Tesseract) are not automatically removed as they may be used by other applications.

#### Windows
```bash
# Remove Java (if installed via Chocolatey)
choco uninstall openjdk

# Remove Tesseract (if installed via Chocolatey)
choco uninstall tesseract
```

#### macOS
```bash
# Remove Java
brew uninstall openjdk@11

# Remove Tesseract
brew uninstall tesseract
```

#### Linux
```bash
# Remove Java
sudo apt remove openjdk-11-jdk

# Remove Tesseract
sudo apt remove tesseract-ocr
```

---

**For additional help, visit our [GitHub repository](https://github.com/your-username/unified-lighting-analyzer) or contact [Short Circuit Company](mailto:Scc@shortcircuitcompany.com).**
