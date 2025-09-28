"""
Configuration settings for the Unified Lighting Analyzer
"""
import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ExtractionConfig:
    """Configuration for PDF extraction methods"""
    # PDF extraction methods
    use_pdfplumber: bool = True
    use_pymupdf: bool = True
    use_pdfminer: bool = True
    
    # Table extraction
    use_camelot: bool = True
    use_tabula: bool = True
    camelot_flavors: List[str] = None
    
    # OCR settings
    use_ocr: bool = True
    tesseract_cmd: Optional[str] = None
    ocr_dpi: int = 300
    ocr_config: str = "--oem 3 --psm 6"
    
    # Quality thresholds
    min_table_score: float = 0.3
    min_rows: int = 2
    min_cols: int = 2
    duplicate_similarity_threshold: float = 0.8
    
    def __post_init__(self):
        if self.camelot_flavors is None:
            self.camelot_flavors = ["lattice", "stream"]

@dataclass
class StandardsConfig:
    """Configuration for lighting standards processing"""
    # Supported standards
    supported_standards: List[str] = None
    
    # Standards database paths
    standards_dir: str = "data/standards"
    standards_db_path: str = "data/standards_db.json"
    
    # Comparison settings
    similarity_threshold: float = 0.7
    compliance_threshold: float = 0.8
    
    def __post_init__(self):
        if self.supported_standards is None:
            self.supported_standards = [
                "EN_12464_1",
                "BREEAM",
                "IES",
                "CIE",
                "ISO_8995"
            ]

@dataclass
class DialuxConfig:
    """Configuration for Dialux report analysis"""
    # Parameter extraction patterns
    extract_illuminance: bool = True
    extract_uniformity: bool = True
    extract_ugr: bool = True
    extract_power_density: bool = True
    extract_color_properties: bool = True
    
    # Room analysis
    min_room_area: float = 1.0  # m²
    max_room_area: float = 10000.0  # m²
    
    # Compliance checking
    check_illuminance_compliance: bool = True
    check_uniformity_compliance: bool = True
    check_glare_compliance: bool = True
    check_power_compliance: bool = True
    
    # Output settings
    generate_detailed_reports: bool = True
    include_visualizations: bool = True
    export_formats: List[str] = None
    
    # Directory settings
    standards_dir: str = "data/standards"
    dialux_output_dir: str = "data/standards/dialux_reports"
    
    def __post_init__(self):
        if self.export_formats is None:
            self.export_formats = ["json", "csv", "xlsx", "pdf"]

@dataclass
class WebConfig:
    """Configuration for web interface"""
    # Server settings
    host: str = "localhost"
    port: int = 8501
    debug: bool = False
    
    # UI settings
    page_title: str = "Unified Lighting Analyzer"
    page_icon: str = "💡"
    layout: str = "wide"
    
    # File upload
    max_file_size: int = 100  # MB
    allowed_extensions: List[str] = None
    
    def __post_init__(self):
        if self.allowed_extensions is None:
            self.allowed_extensions = ["pdf", "txt", "docx"]

@dataclass
class AppConfig:
    """Main application configuration"""
    # Project paths
    project_root: Path = Path(__file__).parent.parent.parent
    data_dir: Path = None
    logs_dir: Path = None
    outputs_dir: Path = None
    dialux_output_dir: str = "data/standards/dialux_reports"
    
    # Component configs
    extraction: ExtractionConfig = None
    standards: StandardsConfig = None
    dialux: DialuxConfig = None
    web: WebConfig = None
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "app.log"
    
    def __post_init__(self):
        if self.data_dir is None:
            self.data_dir = self.project_root / "data"
        if self.logs_dir is None:
            self.logs_dir = self.project_root / "logs"
        if self.outputs_dir is None:
            self.outputs_dir = self.project_root / "data" / "outputs"
        
        if self.extraction is None:
            self.extraction = ExtractionConfig()
        if self.standards is None:
            self.standards = StandardsConfig()
        if self.dialux is None:
            self.dialux = DialuxConfig()
        if self.web is None:
            self.web = WebConfig()
        
        # Create directories
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        self.outputs_dir.mkdir(exist_ok=True)

# Global configuration instance
config = AppConfig()

# Environment variable overrides
def load_config_from_env():
    """Load configuration from environment variables"""
    if os.getenv("TESSERACT_CMD"):
        config.extraction.tesseract_cmd = os.getenv("TESSERACT_CMD")
    
    if os.getenv("LOG_LEVEL"):
        config.log_level = os.getenv("LOG_LEVEL")
    
    if os.getenv("WEB_HOST"):
        config.web.host = os.getenv("WEB_HOST")
    
    if os.getenv("WEB_PORT"):
        config.web.port = int(os.getenv("WEB_PORT"))

# Load environment configuration
load_config_from_env()
