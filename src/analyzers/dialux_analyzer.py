"""
Dialux Report Analysis and Compliance Checking
Comprehensive analysis of Dialux reports against lighting standards
"""
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

import pandas as pd
import numpy as np

try:
    from ..core.config import config
    from ..extractors.pdf_extractor import PDFExtractor
    from ..extractors.table_extractor import AdvancedTableExtractor
    from ..standards.standards_processor import StandardsProcessor, RoomType, StandardType, ComplianceResult
except ImportError:
    from core.config import config
    from extractors.pdf_extractor import PDFExtractor
    from extractors.table_extractor import AdvancedTableExtractor
    from standards.standards_processor import StandardsProcessor, RoomType, StandardType, ComplianceResult

logger = logging.getLogger(__name__)

class DialuxReportType(Enum):
    """Types of Dialux reports"""
    LIGHTING_CALCULATION = "lighting_calculation"
    LUMINAIRE_SCHEDULE = "luminaire_schedule"
    PROJECT_REPORT = "project_report"
    COMPREHENSIVE = "comprehensive"

@dataclass
class DialuxParameter:
    """Extracted Dialux parameter"""
    name: str
    value: float
    unit: str
    room_name: str
    confidence: float
    extraction_method: str
    page_number: int
    raw_text: str = ""

@dataclass
class DialuxRoom:
    """Dialux room analysis"""
    name: str
    area: float
    room_type: RoomType
    
    # Core lighting parameters
    illuminance_avg: Optional[float] = None
    illuminance_min: Optional[float] = None
    illuminance_max: Optional[float] = None
    uniformity: Optional[float] = None
    ugr: Optional[float] = None
    power_density: Optional[float] = None
    
    # Additional parameters
    color_temperature: Optional[float] = None
    color_rendering_index: Optional[float] = None
    luminous_efficacy: Optional[float] = None
    mounting_height: Optional[float] = None
    
    # Data quality
    data_completeness: float = 0.0
    confidence_score: float = 0.0
    
    # Compliance results
    compliance_results: List[ComplianceResult] = None
    
    def __post_init__(self):
        if self.compliance_results is None:
            self.compliance_results = []

@dataclass
class DialuxReport:
    """Complete Dialux report analysis"""
    project_name: str
    report_type: DialuxReportType
    total_rooms: int
    total_area: float
    
    # Overall statistics
    overall_illuminance_avg: float = 0.0
    overall_uniformity_avg: float = 0.0
    overall_ugr_avg: float = 0.0
    overall_power_density_avg: float = 0.0
    
    # Compliance statistics
    overall_compliance_rate: float = 0.0
    data_quality_score: float = 0.0
    
    # Detailed room data
    rooms: List[DialuxRoom] = None
    
    # Standards analysis
    applicable_standards: List[StandardType] = None
    best_matching_standard: Optional[StandardType] = None
    standards_compliance: Dict[str, float] = None
    
    # Analysis metadata
    processing_date: datetime = None
    extraction_confidence: float = 0.0
    
    def __post_init__(self):
        if self.rooms is None:
            self.rooms = []
        if self.applicable_standards is None:
            self.applicable_standards = []
        if self.standards_compliance is None:
            self.standards_compliance = {}
        if self.processing_date is None:
            self.processing_date = datetime.now()

@dataclass
class DialuxAnalysisResult:
    """Complete analysis result for Dialux report"""
    report: DialuxReport
    compliance_summary: Dict[str, Any]
    recommendations: List[str]
    critical_issues: List[str]
    export_paths: Dict[str, str]

class DialuxAnalyzer:
    """Comprehensive Dialux report analyzer"""
    
    def __init__(self):
        self.config = config.dialux
        self.pdf_extractor = PDFExtractor()
        self.table_extractor = AdvancedTableExtractor()
        self.standards_processor = StandardsProcessor()
        self._setup_dialux_patterns()
    
    def _setup_dialux_patterns(self):
        """Setup regex patterns for Dialux parameter extraction"""
        self.patterns = {
            'illuminance_avg': [
                r'(?:average|avg|mean|e\s*avg|em)[:\s]*(\d+(?:\.\d+)?)\s*(?:lux|lx)',
                r'(\d+(?:\.\d+)?)\s*(?:lux|lx)\s*(?:average|avg|mean)',
                r'illuminance[:\s]*(\d+(?:\.\d+)?)\s*(?:lux|lx)',
                r'e[:\s]*(\d+(?:\.\d+)?)\s*(?:lux|lx)',
                r'(\d+(?:\.\d+)?)\s*(?:lux|lx)(?:\s*\(avg\))?'
            ],
            'illuminance_min': [
                r'(?:minimum|min|e\s*min)[:\s]*(\d+(?:\.\d+)?)\s*(?:lux|lx)',
                r'(\d+(?:\.\d+)?)\s*(?:lux|lx)\s*(?:minimum|min)',
                r'(\d+(?:\.\d+)?)\s*(?:lux|lx)\s*\(min\)'
            ],
            'illuminance_max': [
                r'(?:maximum|max|e\s*max)[:\s]*(\d+(?:\.\d+)?)\s*(?:lux|lx)',
                r'(\d+(?:\.\d+)?)\s*(?:lux|lx)\s*(?:maximum|max)',
                r'(\d+(?:\.\d+)?)\s*(?:lux|lx)\s*\(max\)'
            ],
            'uniformity': [
                r'(?:uniformity|uniform|u0)[:\s]*(\d+(?:\.\d+)?)',
                r'(\d+(?:\.\d+)?)\s*(?:uniformity|uniform)',
                r'(\d+(?:\.\d+)?)\s*\(uniformity\)',
                r'u0[:\s]*(\d+(?:\.\d+)?)'
            ],
            'ugr': [
                r'ugr[:\s]*(\d+(?:\.\d+)?)',
                r'unified glare rating[:\s]*(\d+(?:\.\d+)?)',
                r'glare[:\s]*(\d+(?:\.\d+)?)',
                r'(\d+(?:\.\d+)?)\s*(?:ugr|glare)'
            ],
            'power_density': [
                r'(\d+(?:\.\d+)?)\s*(?:w/m²|watt/m²|w/m2)',
                r'power density[:\s]*(\d+(?:\.\d+)?)',
                r'lighting power density[:\s]*(\d+(?:\.\d+)?)',
                r'(\d+(?:\.\d+)?)\s*(?:w/m²|w/m2)'
            ],
            'color_temperature': [
                r'(\d+(?:\.\d+)?)\s*(?:k|kelvin)',
                r'color temperature[:\s]*(\d+(?:\.\d+)?)',
                r'correlated color temperature[:\s]*(\d+(?:\.\d+)?)',
                r'(\d+(?:\.\d+)?)\s*k'
            ],
            'cri': [
                r'cri[:\s]*(\d+(?:\.\d+)?)',
                r'color rendering index[:\s]*(\d+(?:\.\d+)?)',
                r'ra[:\s]*(\d+(?:\.\d+)?)',
                r'(\d+(?:\.\d+)?)\s*(?:cri|ra)'
            ],
            'luminous_efficacy': [
                r'(\d+(?:\.\d+)?)\s*(?:lm/w|lumen/watt)',
                r'luminous efficacy[:\s]*(\d+(?:\.\d+)?)',
                r'efficacy[:\s]*(\d+(?:\.\d+)?)',
                r'(\d+(?:\.\d+)?)\s*(?:lm/w)'
            ],
            'area': [
                r'(\d+(?:\.\d+)?)\s*(?:m²|m2|square meter)',
                r'area[:\s]*(\d+(?:\.\d+)?)',
                r'surface[:\s]*(\d+(?:\.\d+)?)',
                r'(\d+(?:\.\d+)?)\s*(?:m²|m2)'
            ],
            'mounting_height': [
                r'(\d+(?:\.\d+)?)\s*(?:m|meter)',
                r'height[:\s]*(\d+(?:\.\d+)?)',
                r'mounting[:\s]*(\d+(?:\.\d+)?)',
                r'(\d+(?:\.\d+)?)\s*m'
            ]
        }
        
        # Room identification patterns
        self.room_patterns = {
            'office': [r'office', r'workplace', r'work\s+place', r'desk', r'workstation'],
            'meeting_room': [r'meeting', r'conference', r'boardroom', r'seminar'],
            'corridor': [r'corridor', r'passage', r'circulation', r'hallway', r'aisle'],
            'storage': [r'storage', r'warehouse', r'archive', r'stock', r'depot'],
            'industrial': [r'industrial', r'factory', r'manufacturing', r'production', r'workshop'],
            'retail': [r'retail', r'shop', r'store', r'commercial', r'showroom'],
            'educational': [r'classroom', r'school', r'education', r'teaching', r'lecture'],
            'healthcare': [r'hospital', r'medical', r'healthcare', r'clinic', r'treatment'],
            'residential': [r'residential', r'home', r'apartment', r'dwelling', r'living'],
            'outdoor': [r'outdoor', r'exterior', r'external', r'street', r'parking']
        }
    
    def analyze_dialux_report(self, pdf_path: Union[str, Path]) -> DialuxAnalysisResult:
        """
        Analyze a Dialux report comprehensively
        
        Args:
            pdf_path: Path to Dialux PDF report
            
        Returns:
            Complete analysis result
        """
        pdf_path = Path(pdf_path)
        logger.info(f"Starting Dialux analysis: {pdf_path}")
        
        # Extract content from PDF
        extraction_result = self.pdf_extractor.extract_from_pdf(pdf_path)
        
        # Extract tables
        tables = self.table_extractor.extract_tables_from_pdf(pdf_path)
        
        # Identify report type
        report_type = self._identify_report_type(extraction_result.text)
        
        # Extract project information
        project_name = self._extract_project_name(extraction_result.text, pdf_path.name)
        
        # Extract room data
        rooms = self._extract_room_data(extraction_result.text, tables)
        
        # Calculate overall statistics
        overall_stats = self._calculate_overall_statistics(rooms)
        
        # Determine applicable standards
        applicable_standards = self._determine_applicable_standards(rooms)
        best_standard = self._select_best_standard(rooms, applicable_standards)
        
        # Check compliance
        compliance_results = self._check_compliance(rooms, best_standard)
        
        # Create Dialux report
        dialux_report = DialuxReport(
            project_name=project_name,
            report_type=report_type,
            total_rooms=len(rooms),
            total_area=sum(room.area for room in rooms),
            overall_illuminance_avg=overall_stats['illuminance_avg'],
            overall_uniformity_avg=overall_stats['uniformity_avg'],
            overall_ugr_avg=overall_stats['ugr_avg'],
            overall_power_density_avg=overall_stats['power_density_avg'],
            overall_compliance_rate=overall_stats['compliance_rate'],
            data_quality_score=overall_stats['data_quality'],
            rooms=rooms,
            applicable_standards=applicable_standards,
            best_matching_standard=best_standard,
            standards_compliance=compliance_results,
            extraction_confidence=extraction_result.confidence_score
        )
        
        # Generate analysis result
        analysis_result = self._generate_analysis_result(dialux_report, pdf_path)
        
        logger.info(f"Dialux analysis completed: {len(rooms)} rooms, {overall_stats['compliance_rate']:.1%} compliance")
        return analysis_result
    
    def _identify_report_type(self, text: str) -> DialuxReportType:
        """Identify the type of Dialux report"""
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in ['luminaire', 'fixture', 'schedule', 'list']):
            return DialuxReportType.LUMINAIRE_SCHEDULE
        elif any(keyword in text_lower for keyword in ['calculation', 'lighting calculation', 'illuminance']):
            return DialuxReportType.LIGHTING_CALCULATION
        elif any(keyword in text_lower for keyword in ['project', 'report', 'summary']):
            return DialuxReportType.PROJECT_REPORT
        else:
            return DialuxReportType.COMPREHENSIVE
    
    def _extract_project_name(self, text: str, filename: str) -> str:
        """Extract project name from text or filename"""
        # Try to find project name in text
        project_patterns = [
            r'project[:\s]+([^\n\r]+)',
            r'building[:\s]+([^\n\r]+)',
            r'facility[:\s]+([^\n\r]+)',
            r'title[:\s]+([^\n\r]+)'
        ]
        
        for pattern in project_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback to filename
        return Path(filename).stem
    
    def _extract_room_data(self, text: str, tables: List) -> List[DialuxRoom]:
        """Extract room data from text and tables"""
        rooms = []
        
        # Find room sections in text
        room_sections = self._find_room_sections(text)
        
        for room_section in room_sections:
            room_name = room_section['name']
            room_text = room_section['text']
            
            # Determine room type
            room_type = self._determine_room_type(room_name, room_text)
            
            # Extract parameters
            parameters = self._extract_parameters_from_text(room_text)
            
            # Extract area
            area = self._extract_area(room_text, parameters)
            
            # Create room object
            room = DialuxRoom(
                name=room_name,
                area=area,
                room_type=room_type,
                illuminance_avg=parameters.get('illuminance_avg'),
                illuminance_min=parameters.get('illuminance_min'),
                illuminance_max=parameters.get('illuminance_max'),
                uniformity=parameters.get('uniformity'),
                ugr=parameters.get('ugr'),
                power_density=parameters.get('power_density'),
                color_temperature=parameters.get('color_temperature'),
                color_rendering_index=parameters.get('cri'),
                luminous_efficacy=parameters.get('luminous_efficacy'),
                mounting_height=parameters.get('mounting_height')
            )
            
            # Calculate data quality
            room.data_completeness = self._calculate_data_completeness(room)
            room.confidence_score = self._calculate_confidence_score(parameters)
            
            rooms.append(room)
        
        # If no rooms found, try to extract from tables
        if not rooms:
            rooms = self._extract_rooms_from_tables(tables)
        
        return rooms
    
    def _find_room_sections(self, text: str) -> List[Dict[str, str]]:
        """Find room sections in text"""
        room_sections = []
        
        # Look for room headers
        room_header_patterns = [
            r'(?:room|space|area|zone)[:\s]+([^\n\r]+)',
            r'([^\n\r]+)\s*\([^)]*room[^)]*\)',
            r'([^\n\r]+)\s*\([^)]*space[^)]*\)',
            r'building[:\s]+([^\n\r]+)',
            r'floor[:\s]+([^\n\r]+)'
        ]
        
        lines = text.split('\n')
        current_room = None
        current_text = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line is a room header
            is_room_header = False
            for pattern in room_header_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    # Save previous room if exists
                    if current_room:
                        room_sections.append({
                            'name': current_room,
                            'text': '\n'.join(current_text)
                        })
                    
                    # Start new room
                    current_room = match.group(1).strip()
                    current_text = [line]
                    is_room_header = True
                    break
            
            if not is_room_header and current_room:
                current_text.append(line)
        
        # Add last room
        if current_room:
            room_sections.append({
                'name': current_room,
                'text': '\n'.join(current_text)
            })
        
        return room_sections
    
    def _determine_room_type(self, room_name: str, room_text: str) -> RoomType:
        """Determine room type from name and text"""
        text_to_check = f"{room_name} {room_text}".lower()
        
        for room_type, patterns in self.room_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_to_check):
                    return RoomType(room_type)
        
        return RoomType.OFFICE  # Default
    
    def _extract_parameters_from_text(self, text: str) -> Dict[str, float]:
        """Extract lighting parameters from text"""
        parameters = {}
        
        for param_name, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    try:
                        value = float(match.group(1))
                        parameters[param_name] = value
                        break  # Take first match
                    except (ValueError, IndexError):
                        continue
        
        return parameters
    
    def _extract_area(self, text: str, parameters: Dict[str, float]) -> float:
        """Extract room area"""
        if 'area' in parameters:
            return parameters['area']
        
        # Try to find area in text
        area_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:m²|m2|square meter)',
            r'area[:\s]*(\d+(?:\.\d+)?)',
            r'surface[:\s]*(\d+(?:\.\d+)?)'
        ]
        
        for pattern in area_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        
        return 0.0  # Default area
    
    def _extract_rooms_from_tables(self, tables: List) -> List[DialuxRoom]:
        """Extract room data from tables if text extraction failed"""
        rooms = []
        
        for table in tables:
            if table.dataframe.empty:
                continue
            
            # Look for room data in table
            room_data = self._extract_room_data_from_table(table.dataframe)
            if room_data:
                rooms.extend(room_data)
        
        return rooms
    
    def _extract_room_data_from_table(self, df: pd.DataFrame) -> List[DialuxRoom]:
        """Extract room data from a single table"""
        rooms = []
        
        # Look for room names in first column or headers
        room_names = []
        if not df.empty:
            # Check first column for room names
            first_col = df.iloc[:, 0].astype(str)
            for name in first_col:
                if self._looks_like_room_name(name):
                    room_names.append(name)
        
        # If no room names found, create a generic room
        if not room_names:
            room_names = ["General Room"]
        
        # Extract parameters for each room
        for room_name in room_names:
            parameters = self._extract_parameters_from_table(df, room_name)
            
            room = DialuxRoom(
                name=room_name,
                area=parameters.get('area', 0.0),
                room_type=self._determine_room_type(room_name, ""),
                illuminance_avg=parameters.get('illuminance_avg'),
                illuminance_min=parameters.get('illuminance_min'),
                illuminance_max=parameters.get('illuminance_max'),
                uniformity=parameters.get('uniformity'),
                ugr=parameters.get('ugr'),
                power_density=parameters.get('power_density'),
                color_temperature=parameters.get('color_temperature'),
                color_rendering_index=parameters.get('cri'),
                luminous_efficacy=parameters.get('luminous_efficacy'),
                mounting_height=parameters.get('mounting_height')
            )
            
            room.data_completeness = self._calculate_data_completeness(room)
            room.confidence_score = self._calculate_confidence_score(parameters)
            
            rooms.append(room)
        
        return rooms
    
    def _looks_like_room_name(self, text: str) -> bool:
        """Check if text looks like a room name"""
        if not text or len(text.strip()) < 3:
            return False
        
        text_lower = text.lower()
        
        # Check for room-related keywords
        room_keywords = ['room', 'space', 'area', 'zone', 'office', 'meeting', 'corridor', 'storage']
        if any(keyword in text_lower for keyword in room_keywords):
            return True
        
        # Check for building/floor references
        building_keywords = ['building', 'floor', 'level', 'story']
        if any(keyword in text_lower for keyword in building_keywords):
            return True
        
        return False
    
    def _extract_parameters_from_table(self, df: pd.DataFrame, room_name: str) -> Dict[str, float]:
        """Extract parameters from table for a specific room"""
        parameters = {}
        
        # Convert dataframe to text for pattern matching
        table_text = df.to_string()
        
        # Extract parameters using patterns
        for param_name, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, table_text, re.IGNORECASE)
                for match in matches:
                    try:
                        value = float(match.group(1))
                        parameters[param_name] = value
                        break
                    except (ValueError, IndexError):
                        continue
        
        return parameters
    
    def _calculate_data_completeness(self, room: DialuxRoom) -> float:
        """Calculate data completeness score for a room"""
        total_params = 8  # Core parameters
        found_params = 0
        
        if room.illuminance_avg is not None:
            found_params += 1
        if room.uniformity is not None:
            found_params += 1
        if room.ugr is not None:
            found_params += 1
        if room.power_density is not None:
            found_params += 1
        if room.color_temperature is not None:
            found_params += 1
        if room.color_rendering_index is not None:
            found_params += 1
        if room.luminous_efficacy is not None:
            found_params += 1
        if room.area > 0:
            found_params += 1
        
        return found_params / total_params
    
    def _calculate_confidence_score(self, parameters: Dict[str, float]) -> float:
        """Calculate confidence score for extracted parameters"""
        if not parameters:
            return 0.0
        
        # Base confidence on number of parameters found
        param_count = len(parameters)
        max_params = len(self.patterns)
        
        return min(1.0, param_count / max_params)
    
    def _calculate_overall_statistics(self, rooms: List[DialuxRoom]) -> Dict[str, float]:
        """Calculate overall statistics for all rooms"""
        if not rooms:
            return {
                'illuminance_avg': 0.0,
                'uniformity_avg': 0.0,
                'ugr_avg': 0.0,
                'power_density_avg': 0.0,
                'compliance_rate': 0.0,
                'data_quality': 0.0
            }
        
        # Calculate averages
        illuminance_values = [r.illuminance_avg for r in rooms if r.illuminance_avg is not None]
        uniformity_values = [r.uniformity for r in rooms if r.uniformity is not None]
        ugr_values = [r.ugr for r in rooms if r.ugr is not None]
        power_values = [r.power_density for r in rooms if r.power_density is not None]
        
        illuminance_avg = np.mean(illuminance_values) if illuminance_values else 0.0
        uniformity_avg = np.mean(uniformity_values) if uniformity_values else 0.0
        ugr_avg = np.mean(ugr_values) if ugr_values else 0.0
        power_density_avg = np.mean(power_values) if power_values else 0.0
        
        # Calculate data quality
        data_quality = np.mean([r.data_completeness for r in rooms])
        
        # Calculate compliance rate (placeholder - will be updated after compliance checking)
        compliance_rate = 0.0
        
        return {
            'illuminance_avg': illuminance_avg,
            'uniformity_avg': uniformity_avg,
            'ugr_avg': ugr_avg,
            'power_density_avg': power_density_avg,
            'compliance_rate': compliance_rate,
            'data_quality': data_quality
        }
    
    def _determine_applicable_standards(self, rooms: List[DialuxRoom]) -> List[StandardType]:
        """Determine applicable standards based on room types"""
        applicable = []
        
        # Check room types and determine standards
        room_types = set(room.room_type for room in rooms)
        
        # EN 12464-1 is applicable for most room types
        if any(rt in [RoomType.OFFICE, RoomType.MEETING_ROOM, RoomType.CORRIDOR, RoomType.STORAGE] for rt in room_types):
            applicable.append(StandardType.EN_12464_1)
        
        # BREEAM for office buildings
        if RoomType.OFFICE in room_types:
            applicable.append(StandardType.BREEAM)
        
        # IES for industrial spaces
        if RoomType.INDUSTRIAL in room_types:
            applicable.append(StandardType.IES)
        
        return applicable if applicable else [StandardType.EN_12464_1]  # Default
    
    def _select_best_standard(self, rooms: List[DialuxRoom], standards: List[StandardType]) -> StandardType:
        """Select the best matching standard"""
        if not standards:
            return StandardType.EN_12464_1
        
        # For now, return the first standard (could be enhanced with scoring)
        return standards[0]
    
    def _check_compliance(self, rooms: List[DialuxRoom], standard: StandardType) -> Dict[str, float]:
        """Check compliance for all rooms against standard"""
        compliance_results = {}
        
        for room in rooms:
            # Prepare actual values
            actual_values = {}
            if room.illuminance_avg is not None:
                actual_values['illuminance'] = room.illuminance_avg
            if room.uniformity is not None:
                actual_values['uniformity'] = room.uniformity
            if room.ugr is not None:
                actual_values['ugr'] = room.ugr
            if room.power_density is not None:
                actual_values['power_density'] = room.power_density
            
            # Check compliance
            room_compliance = self.standards_processor.check_compliance(
                actual_values, room.room_type, standard
            )
            
            room.compliance_results = room_compliance
            
            # Calculate compliance rate for this room
            if room_compliance:
                compliant_count = sum(1 for result in room_compliance if result.is_compliant)
                room_compliance_rate = compliant_count / len(room_compliance)
            else:
                room_compliance_rate = 0.0
            
            compliance_results[room.name] = room_compliance_rate
        
        return compliance_results
    
    def _generate_analysis_result(self, report: DialuxReport, pdf_path: Path) -> DialuxAnalysisResult:
        """Generate complete analysis result"""
        # Calculate overall compliance rate
        if report.standards_compliance:
            overall_compliance = np.mean(list(report.standards_compliance.values()))
            report.overall_compliance_rate = overall_compliance
        
        # Generate compliance summary
        compliance_summary = self._generate_compliance_summary(report)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(report)
        
        # Identify critical issues
        critical_issues = self._identify_critical_issues(report)
        
        # Export results
        export_paths = self._export_analysis_results(report, pdf_path)
        
        return DialuxAnalysisResult(
            report=report,
            compliance_summary=compliance_summary,
            recommendations=recommendations,
            critical_issues=critical_issues,
            export_paths=export_paths
        )
    
    def _generate_compliance_summary(self, report: DialuxReport) -> Dict[str, Any]:
        """Generate compliance summary"""
        summary = {
            "overall_compliance_rate": report.overall_compliance_rate,
            "total_rooms": report.total_rooms,
            "compliant_rooms": 0,
            "non_compliant_rooms": 0,
            "room_compliance": {},
            "parameter_compliance": {
                "illuminance": {"compliant": 0, "total": 0},
                "uniformity": {"compliant": 0, "total": 0},
                "ugr": {"compliant": 0, "total": 0},
                "power_density": {"compliant": 0, "total": 0}
            }
        }
        
        for room in report.rooms:
            room_compliant = True
            for result in room.compliance_results:
                if not result.is_compliant:
                    room_compliant = False
                
                # Count parameter compliance
                param = result.parameter
                if param in summary["parameter_compliance"]:
                    summary["parameter_compliance"][param]["total"] += 1
                    if result.is_compliant:
                        summary["parameter_compliance"][param]["compliant"] += 1
            
            summary["room_compliance"][room.name] = room_compliant
            if room_compliant:
                summary["compliant_rooms"] += 1
            else:
                summary["non_compliant_rooms"] += 1
        
        return summary
    
    def _generate_recommendations(self, report: DialuxReport) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Overall recommendations
        if report.overall_compliance_rate < 0.8:
            recommendations.append("Overall compliance is below 80%. Consider reviewing lighting design.")
        
        if report.data_quality_score < 0.7:
            recommendations.append("Data quality is low. Verify parameter extraction accuracy.")
        
        # Room-specific recommendations
        for room in report.rooms:
            if room.data_completeness < 0.5:
                recommendations.append(f"Room '{room.name}' has incomplete data. Verify all parameters are extracted.")
            
            for result in room.compliance_results:
                if not result.is_compliant:
                    if result.parameter == 'illuminance' and result.actual_value < result.required_value:
                        recommendations.append(f"Increase illuminance in '{room.name}' to meet {result.required_value} lux requirement")
                    elif result.parameter == 'uniformity' and result.actual_value < result.required_value:
                        recommendations.append(f"Improve uniformity in '{room.name}' to meet {result.required_value} requirement")
                    elif result.parameter == 'ugr' and result.actual_value > result.required_value:
                        recommendations.append(f"Reduce glare in '{room.name}' to meet UGR {result.required_value} requirement")
                    elif result.parameter == 'power_density' and result.actual_value > result.required_value:
                        recommendations.append(f"Reduce power density in '{room.name}' to meet {result.required_value} W/m² requirement")
        
        return recommendations
    
    def _identify_critical_issues(self, report: DialuxReport) -> List[str]:
        """Identify critical issues that need immediate attention"""
        critical_issues = []
        
        for room in report.rooms:
            for result in room.compliance_results:
                if not result.is_compliant:
                    # Check if deviation is critical
                    if result.parameter == 'illuminance' and result.actual_value < result.required_value * 0.5:
                        critical_issues.append(f"CRITICAL: Illuminance in '{room.name}' is less than 50% of requirement")
                    elif result.parameter == 'uniformity' and result.actual_value < 0.3:
                        critical_issues.append(f"CRITICAL: Very poor uniformity in '{room.name}' ({result.actual_value})")
                    elif result.parameter == 'ugr' and result.actual_value > 25:
                        critical_issues.append(f"CRITICAL: Excessive glare in '{room.name}' (UGR {result.actual_value})")
        
        return critical_issues
    
    def _export_analysis_results(self, report: DialuxReport, pdf_path: Path) -> Dict[str, str]:
        """Export analysis results to various formats"""
        output_dir = Path(self.config.dialux_output_dir)
        output_dir.mkdir(exist_ok=True)
        
        base_name = pdf_path.stem
        export_paths = {}
        
        # Export JSON
        json_path = output_dir / f"{base_name}_analysis.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(report), f, indent=2, ensure_ascii=False, default=str)
        export_paths["json"] = str(json_path)
        
        # Export CSV summary
        csv_path = output_dir / f"{base_name}_summary.csv"
        summary_data = []
        for room in report.rooms:
            summary_data.append({
                "room_name": room.name,
                "room_type": room.room_type.value,
                "area": room.area,
                "illuminance_avg": room.illuminance_avg,
                "uniformity": room.uniformity,
                "ugr": room.ugr,
                "power_density": room.power_density,
                "data_completeness": room.data_completeness,
                "confidence_score": room.confidence_score
            })
        
        df = pd.DataFrame(summary_data)
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        export_paths["csv"] = str(csv_path)
        
        return export_paths
