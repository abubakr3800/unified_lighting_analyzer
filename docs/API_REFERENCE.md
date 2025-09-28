# API Reference - Unified Lighting Analyzer

## 📋 Table of Contents

1. [Core Classes](#core-classes)
2. [Extractors](#extractors)
3. [Analyzers](#analyzers)
4. [Standards](#standards)
5. [Data Classes](#data-classes)
6. [Configuration](#configuration)
7. [Utilities](#utilities)

## 🏗️ Core Classes

### `PDFExtractor`

Main class for PDF text and data extraction using multiple methods.

```python
from src.extractors.pdf_extractor import PDFExtractor

extractor = PDFExtractor()
result = extractor.extract_text_from_pdf("report.pdf")
```

#### Methods

##### `extract_text_from_pdf(pdf_path: Union[str, Path]) -> ExtractionResult`

Extracts text from PDF using multiple methods with fallback strategy.

**Parameters:**
- `pdf_path`: Path to PDF file

**Returns:**
- `ExtractionResult`: Contains text, tables, images, metadata, and confidence score

**Example:**
```python
result = extractor.extract_text_from_pdf("report.pdf")
print(f"Extracted {len(result.text)} characters")
print(f"Found {len(result.tables)} tables")
print(f"Confidence: {result.confidence_score:.2%}")
```

### `AdvancedTableExtractor`

Advanced table extraction with quality analysis and duplicate detection.

```python
from src.extractors.table_extractor import AdvancedTableExtractor

extractor = AdvancedTableExtractor()
tables = extractor.extract_tables("report.pdf")
```

#### Methods

##### `extract_tables(pdf_path: Union[str, Path]) -> List[pd.DataFrame]`

Extracts tables from PDF using multiple methods with quality filtering.

**Parameters:**
- `pdf_path`: Path to PDF file

**Returns:**
- `List[pd.DataFrame]`: List of high-quality unique tables

**Example:**
```python
tables = extractor.extract_tables("report.pdf")
for i, table in enumerate(tables):
    print(f"Table {i+1}: {table.shape[0]} rows, {table.shape[1]} columns")
```

## 🔍 Extractors

### `FocusedExtractor`

Fast extractor for essential Dialux data using regex patterns.

```python
from src.extractors.focused_extractor import FocusedExtractor

extractor = FocusedExtractor(api_key="sk-...")
result = extractor.extract_focused_data("report.pdf")
```

#### Methods

##### `extract_focused_data(pdf_path: Union[str, Path]) -> FocusedExtractionResult`

Extracts essential data quickly using regex patterns and optional OpenAI.

**Parameters:**
- `pdf_path`: Path to PDF file

**Returns:**
- `FocusedExtractionResult`: Contains project info, room data, and processing time

**Example:**
```python
result = extractor.extract_focused_data("report.pdf")
print(f"Project: {result.project_name}")
print(f"Total Area: {result.total_area} m²")
print(f"Processing Time: {result.processing_time:.2f}s")
```

### `OpenAIExtractor`

AI-powered extractor for comprehensive data extraction using OpenAI GPT models.

```python
from src.extractors.openai_extractor import OpenAIExtractor

extractor = OpenAIExtractor(api_key="sk-...")
result = extractor.extract_data(text)
```

#### Methods

##### `extract_data(text: str) -> ExtractedReportData`

Extracts structured data from text using OpenAI GPT models.

**Parameters:**
- `text`: Raw text from PDF

**Returns:**
- `ExtractedReportData`: Comprehensive extracted data with metadata

**Example:**
```python
result = extractor.extract_data(pdf_text)
print(f"Company: {result.project_company}")
print(f"Manufacturer: {result.luminaire_manufacturer}")
print(f"Driver: {result.driver_circuit_company}")
```

## 🏢 Analyzers

### `FastDialuxAnalyzer`

Fast analyzer for Dialux reports with focused extraction and standards comparison.

```python
from src.analyzers.fast_dialux_analyzer import FastDialuxAnalyzer

analyzer = FastDialuxAnalyzer(api_key="sk-...")
result = analyzer.analyze_dialux_report("report.pdf")
```

#### Methods

##### `analyze_dialux_report(pdf_path: Union[str, Path]) -> FastDialuxAnalysisResult`

Performs fast analysis of Dialux report with comprehensive results.

**Parameters:**
- `pdf_path`: Path to PDF file

**Returns:**
- `FastDialuxAnalysisResult`: Complete analysis with recommendations and critical issues

**Example:**
```python
result = analyzer.analyze_dialux_report("report.pdf")
print(f"Compliance: {result.report.overall_compliance_rate:.1%}")
print(f"Recommendations: {len(result.recommendations)}")
print(f"Critical Issues: {len(result.critical_issues)}")
```

### `EnhancedDialuxAnalyzer`

Enhanced analyzer using OpenAI for comprehensive extraction and analysis.

```python
from src.analyzers.enhanced_dialux_analyzer import EnhancedDialuxAnalyzer

analyzer = EnhancedDialuxAnalyzer(api_key="sk-...")
result = analyzer.analyze_dialux_report("report.pdf")
```

#### Methods

##### `analyze_dialux_report(pdf_path: Union[str, Path]) -> EnhancedDialuxAnalysisResult`

Performs comprehensive analysis using OpenAI for detailed extraction.

**Parameters:**
- `pdf_path`: Path to PDF file

**Returns:**
- `EnhancedDialuxAnalysisResult`: Enhanced analysis with detailed metadata

**Example:**
```python
result = analyzer.analyze_dialux_report("report.pdf")
print(f"Data Quality: {result.report.data_quality_score:.1%}")
print(f"Processing Time: {result.processing_time:.2f}s")
```

### `DialuxAnalyzer`

Standard analyzer with multi-method extraction and comprehensive analysis.

```python
from src.analyzers.dialux_analyzer import DialuxAnalyzer

analyzer = DialuxAnalyzer()
result = analyzer.analyze_dialux_report("report.pdf")
```

#### Methods

##### `analyze_dialux_report(pdf_path: Union[str, Path]) -> DialuxAnalysisResult`

Performs standard analysis using multiple extraction methods.

**Parameters:**
- `pdf_path`: Path to PDF file

**Returns:**
- `DialuxAnalysisResult`: Standard analysis results

**Example:**
```python
result = analyzer.analyze_dialux_report("report.pdf")
print(f"Rooms: {len(result.report.rooms)}")
print(f"Export Paths: {result.export_paths}")
```

## 📋 Standards

### `StandardsProcessor`

Processor for lighting standards documents and compliance checking.

```python
from src.standards.standards_processor import StandardsProcessor

processor = StandardsProcessor()
standards = processor.get_standards_for_room_type(RoomType.OFFICE)
```

#### Methods

##### `get_standards_for_room_type(room_type: RoomType) -> Dict[str, Dict[str, Any]]`

Gets standards requirements for a specific room type.

**Parameters:**
- `room_type`: Room type enum (OFFICE, MEETING_ROOM, etc.)

**Returns:**
- `Dict[str, Dict[str, Any]]`: Standards requirements by standard name

**Example:**
```python
standards = processor.get_standards_for_room_type(RoomType.OFFICE)
for standard_name, requirements in standards.items():
    print(f"{standard_name}: {requirements['illuminance_min']} lux")
```

##### `check_compliance(actual_value: float, parameter: str, room_type: RoomType, standard: StandardType) -> ComplianceResult`

Checks compliance of a parameter against standards.

**Parameters:**
- `actual_value`: Actual measured value
- `parameter`: Parameter name (illuminance, uniformity, ugr, power_density)
- `room_type`: Room type enum
- `standard`: Standard type enum

**Returns:**
- `ComplianceResult`: Compliance check result with deviation

**Example:**
```python
result = processor.check_compliance(
    actual_value=520.0,
    parameter="illuminance",
    room_type=RoomType.OFFICE,
    standard=StandardType.EN_12464_1
)
print(f"Compliant: {result.is_compliant}")
print(f"Deviation: {result.deviation}")
```

## 📊 Data Classes

### `ExtractionResult`

Result of PDF extraction with metadata and confidence score.

```python
@dataclass
class ExtractionResult:
    text: str
    tables: List[pd.DataFrame]
    images: List[str]
    metadata: Dict[str, Any]
    extraction_method: str
    confidence_score: float
    processing_time: float = 0.0
```

### `FastRoomAnalysis`

Fast room analysis with compliance results.

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
    
    @property
    def name(self) -> str:
        """Alias for room_name for compatibility"""
        return self.room_name
```

### `ComplianceResult`

Result of compliance checking against standards.

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

### `FastDialuxReport`

Fast Dialux report with project and room information.

```python
@dataclass
class FastDialuxReport:
    project_name: Optional[str] = None
    project_company: Optional[str] = None
    luminaire_manufacturer: Optional[str] = None
    driver_circuit_company: Optional[str] = None
    rooms: List[FastRoomAnalysis] = None
    total_rooms: int = 0
    total_area: float = 0.0
    overall_compliance_rate: float = 0.0
    data_quality_score: float = 0.0
```

### `FastDialuxAnalysisResult`

Complete fast analysis result with recommendations and issues.

```python
@dataclass
class FastDialuxAnalysisResult:
    report: FastDialuxReport
    recommendations: List[str]
    critical_issues: List[str]
    export_paths: Dict[str, str]
    processing_time: float
```

## ⚙️ Configuration

### `AppConfig`

Main application configuration.

```python
@dataclass
class AppConfig:
    project_root: Path = Path(__file__).parent.parent.parent
    data_dir: Path = None
    logs_dir: Path = None
    outputs_dir: Path = None
    dialux_output_dir: str = "data/standards/dialux_reports"
    log_level: str = "INFO"
    log_file: str = "app.log"
```

### `DialuxConfig`

Configuration for Dialux report analysis.

```python
@dataclass
class DialuxConfig:
    extract_illuminance: bool = True
    extract_uniformity: bool = True
    extract_ugr: bool = True
    extract_power_density: bool = True
    extract_color_properties: bool = True
    min_room_area: float = 1.0
    max_room_area: float = 10000.0
    check_illuminance_compliance: bool = True
    check_uniformity_compliance: bool = True
    check_glare_compliance: bool = True
    check_power_compliance: bool = True
    generate_detailed_reports: bool = True
    include_visualizations: bool = True
    export_formats: List[str] = None
    standards_dir: str = "data/standards"
    dialux_output_dir: str = "data/standards/dialux_reports"
```

### `ExtractionConfig`

Configuration for PDF extraction.

```python
@dataclass
class ExtractionConfig:
    use_pdfplumber: bool = True
    use_pymupdf: bool = True
    use_pdfminer: bool = True
    use_ocr: bool = True
    ocr_language: str = "eng"
    table_extraction_methods: List[str] = None
    min_table_confidence: float = 0.5
    max_extraction_time: int = 300
```

## 🔧 Utilities

### `RoomType` Enum

Enumeration of supported room types.

```python
class RoomType(Enum):
    OFFICE = "office"
    MEETING_ROOM = "meeting_room"
    CONFERENCE_ROOM = "conference_room"
    CORRIDOR = "corridor"
    STORAGE = "storage"
    INDUSTRIAL = "industrial"
    RETAIL = "retail"
    EDUCATIONAL = "educational"
    HEALTHCARE = "healthcare"
    RESIDENTIAL = "residential"
    OUTDOOR = "outdoor"
```

### `StandardType` Enum

Enumeration of supported standards.

```python
class StandardType(Enum):
    EN_12464_1 = "EN_12464_1"
    BREEAM = "BREEAM"
    IES = "IES"
    ASHRAE = "ASHRAE"
    CUSTOM = "CUSTOM"
```

## 📝 Usage Examples

### Basic PDF Extraction

```python
from src.extractors.pdf_extractor import PDFExtractor

# Initialize extractor
extractor = PDFExtractor()

# Extract text from PDF
result = extractor.extract_text_from_pdf("report.pdf")

# Access results
print(f"Text length: {len(result.text)}")
print(f"Tables found: {len(result.tables)}")
print(f"Confidence: {result.confidence_score:.2%}")
```

### Fast Dialux Analysis

```python
from src.analyzers.fast_dialux_analyzer import FastDialuxAnalyzer

# Initialize analyzer
analyzer = FastDialuxAnalyzer(api_key="sk-...")

# Analyze report
result = analyzer.analyze_dialux_report("report.pdf")

# Access results
report = result.report
print(f"Project: {report.project_name}")
print(f"Company: {report.project_company}")
print(f"Total Area: {report.total_area} m²")
print(f"Compliance: {report.overall_compliance_rate:.1%}")

# Room analysis
for room in report.rooms:
    print(f"Room: {room.name}")
    print(f"  Area: {room.area} m²")
    print(f"  Illuminance: {room.illuminance_avg} lux")
    print(f"  Uniformity: {room.uniformity}")
    print(f"  UGR: {room.ugr}")

# Recommendations
for i, rec in enumerate(result.recommendations, 1):
    print(f"{i}. {rec}")

# Critical issues
for issue in result.critical_issues:
    print(f"⚠️ {issue}")
```

### Standards Compliance Checking

```python
from src.standards.standards_processor import StandardsProcessor, RoomType, StandardType

# Initialize processor
processor = StandardsProcessor()

# Get standards for office
standards = processor.get_standards_for_room_type(RoomType.OFFICE)

# Check compliance
result = processor.check_compliance(
    actual_value=520.0,
    parameter="illuminance",
    room_type=RoomType.OFFICE,
    standard=StandardType.EN_12464_1
)

print(f"Parameter: {result.parameter}")
print(f"Actual: {result.actual_value} {result.unit}")
print(f"Required: {result.required_value} {result.unit}")
print(f"Compliant: {result.is_compliant}")
print(f"Deviation: {result.deviation} {result.unit}")
```

### Custom Configuration

```python
from src.core.config import AppConfig, DialuxConfig
from pathlib import Path

# Custom configuration
config = AppConfig(
    project_root=Path("./custom_project"),
    outputs_dir=Path("./custom_outputs"),
    log_level="DEBUG"
)

dialux_config = DialuxConfig(
    min_room_area=5.0,
    max_room_area=5000.0,
    check_illuminance_compliance=True,
    check_uniformity_compliance=True,
    check_glare_compliance=True,
    check_power_compliance=True
)
```

### Batch Processing

```python
from pathlib import Path
from src.analyzers.fast_dialux_analyzer import FastDialuxAnalyzer

# Initialize analyzer
analyzer = FastDialuxAnalyzer(api_key="sk-...")

# Process multiple files
pdf_files = Path("./reports").glob("*.pdf")
results = []

for pdf_file in pdf_files:
    print(f"Processing {pdf_file.name}...")
    result = analyzer.analyze_dialux_report(pdf_file)
    results.append(result)
    
    # Save results
    output_dir = Path("./results") / pdf_file.stem
    output_dir.mkdir(exist_ok=True)
    
    # Export to JSON
    import json
    with open(output_dir / "analysis.json", "w") as f:
        json.dump(result.__dict__, f, indent=2, default=str)

print(f"Processed {len(results)} files")
```

## 🔍 Error Handling

### Common Exceptions

```python
from src.extractors.pdf_extractor import PDFExtractionError
from src.analyzers.fast_dialux_analyzer import DialuxAnalysisError

try:
    result = analyzer.analyze_dialux_report("report.pdf")
except DialuxAnalysisError as e:
    print(f"Analysis failed: {e}")
except PDFExtractionError as e:
    print(f"PDF extraction failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Validation

```python
from src.core.validators import validate_pdf_path, validate_room_type

# Validate inputs
try:
    validate_pdf_path("report.pdf")
    validate_room_type("office")
except ValueError as e:
    print(f"Validation error: {e}")
```

---

**For more examples and advanced usage, visit our [GitHub repository](https://github.com/your-username/unified-lighting-analyzer) or contact [Short Circuit Company](mailto:Scc@shortcircuitcompany.com).**
