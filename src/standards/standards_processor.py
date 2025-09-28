"""
Lighting Standards Processing and Comparison
Handles standards documents, compliance checking, and comparison analysis
"""
import json
import re
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
except ImportError:
    from core.config import config
    from extractors.pdf_extractor import PDFExtractor
    from extractors.table_extractor import AdvancedTableExtractor

logger = logging.getLogger(__name__)

class StandardType(Enum):
    """Types of lighting standards"""
    EN_12464_1 = "EN_12464_1"
    BREEAM = "BREEAM"
    IES = "IES"
    CIE = "CIE"
    ISO_8995 = "ISO_8995"
    CUSTOM = "CUSTOM"

class RoomType(Enum):
    """Types of rooms/spaces"""
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

@dataclass
class LightingRequirement:
    """Lighting requirement specification"""
    parameter: str
    value: float
    unit: str
    condition: str  # minimum, maximum, average, etc.
    room_type: RoomType
    standard: StandardType
    description: str = ""
    notes: str = ""

@dataclass
class StandardsDocument:
    """Processed standards document"""
    name: str
    standard_type: StandardType
    version: str
    language: str
    requirements: List[LightingRequirement]
    tables: List[pd.DataFrame]
    text_content: str
    metadata: Dict[str, Any]
    processing_date: datetime

@dataclass
class ComplianceResult:
    """Result of compliance checking"""
    parameter: str
    required_value: float
    actual_value: float
    unit: str
    is_compliant: bool
    compliance_percentage: float
    deviation: float
    room_type: RoomType
    standard: StandardType
    notes: str = ""

@dataclass
class StandardsComparison:
    """Comparison between standards"""
    standard_a: StandardType
    standard_b: StandardType
    room_type: RoomType
    parameter: str
    value_a: float
    value_b: float
    difference: float
    difference_percentage: float
    more_strict: StandardType
    harmonization_recommendation: str

class StandardsProcessor:
    """Processor for lighting standards documents and compliance checking"""
    
    def __init__(self):
        self.config = config.standards
        self.pdf_extractor = PDFExtractor()
        self.table_extractor = AdvancedTableExtractor()
        self.standards_database = self._load_standards_database()
        self._setup_lighting_patterns()
    
    def _setup_lighting_patterns(self):
        """Setup regex patterns for lighting parameter extraction"""
        self.patterns = {
            'illuminance': [
                r'(\d+(?:\.\d+)?)\s*(?:lux|lx)',
                r'illuminance[:\s]*(\d+(?:\.\d+)?)',
                r'lighting level[:\s]*(\d+(?:\.\d+)?)',
                r'(\d+(?:\.\d+)?)\s*(?:lux|lx)\s*(?:minimum|min|maximum|max|average|avg)',
            ],
            'uniformity': [
                r'uniformity[:\s]*(\d+(?:\.\d+)?)',
                r'u0[:\s]*(\d+(?:\.\d+)?)',
                r'(\d+(?:\.\d+)?)\s*(?:uniformity|uniform)',
            ],
            'ugr': [
                r'ugr[:\s]*(\d+(?:\.\d+)?)',
                r'unified glare rating[:\s]*(\d+(?:\.\d+)?)',
                r'glare[:\s]*(\d+(?:\.\d+)?)',
            ],
            'power_density': [
                r'(\d+(?:\.\d+)?)\s*(?:w/m²|watt/m²|w/m2)',
                r'power density[:\s]*(\d+(?:\.\d+)?)',
                r'lighting power density[:\s]*(\d+(?:\.\d+)?)',
            ],
            'color_temperature': [
                r'(\d+(?:\.\d+)?)\s*(?:k|kelvin)',
                r'color temperature[:\s]*(\d+(?:\.\d+)?)',
                r'correlated color temperature[:\s]*(\d+(?:\.\d+)?)',
            ],
            'cri': [
                r'cri[:\s]*(\d+(?:\.\d+)?)',
                r'color rendering index[:\s]*(\d+(?:\.\d+)?)',
                r'ra[:\s]*(\d+(?:\.\d+)?)',
            ]
        }
        
        self.room_patterns = {
            'office': [r'office', r'workplace', r'work\s+place', r'desk'],
            'meeting_room': [r'meeting', r'conference', r'boardroom'],
            'corridor': [r'corridor', r'passage', r'circulation', r'hallway'],
            'storage': [r'storage', r'warehouse', r'archive'],
            'industrial': [r'industrial', r'factory', r'manufacturing', r'production'],
            'retail': [r'retail', r'shop', r'store', r'commercial'],
            'educational': [r'classroom', r'school', r'education', r'teaching'],
            'healthcare': [r'hospital', r'medical', r'healthcare', r'clinic'],
            'residential': [r'residential', r'home', r'apartment', r'dwelling'],
            'outdoor': [r'outdoor', r'exterior', r'external', r'street']
        }
    
    def _load_standards_database(self) -> Dict[str, Any]:
        """Load or create standards database"""
        db_path = Path(self.config.standards_db_path)
        
        if db_path.exists():
            try:
                with open(db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load standards database: {e}")
        
        # Create default database
        default_db = self._create_default_standards_database()
        self._save_standards_database(default_db)
        return default_db
    
    def _create_default_standards_database(self) -> Dict[str, Any]:
        """Create default standards database with common requirements"""
        return {
            "EN_12464_1": {
                "name": "EN 12464-1:2021 - Light and lighting - Lighting of work places",
                "version": "2021",
                "requirements": {
                    "office": {
                        "illuminance_min": 500,
                        "illuminance_unit": "lux",
                        "uniformity_min": 0.6,
                        "ugr_max": 19,
                        "power_density_max": 12,
                        "power_density_unit": "W/m²",
                        "color_temperature_min": 3000,
                        "color_temperature_max": 6500,
                        "color_temperature_unit": "K",
                        "cri_min": 80
                    },
                    "meeting_room": {
                        "illuminance_min": 500,
                        "illuminance_unit": "lux",
                        "uniformity_min": 0.6,
                        "ugr_max": 19,
                        "power_density_max": 12,
                        "power_density_unit": "W/m²",
                        "color_temperature_min": 3000,
                        "color_temperature_max": 6500,
                        "color_temperature_unit": "K",
                        "cri_min": 80
                    },
                    "corridor": {
                        "illuminance_min": 100,
                        "illuminance_unit": "lux",
                        "uniformity_min": 0.4,
                        "ugr_max": 22,
                        "power_density_max": 5,
                        "power_density_unit": "W/m²",
                        "color_temperature_min": 3000,
                        "color_temperature_max": 6500,
                        "color_temperature_unit": "K",
                        "cri_min": 80
                    },
                    "storage": {
                        "illuminance_min": 200,
                        "illuminance_unit": "lux",
                        "uniformity_min": 0.4,
                        "ugr_max": 25,
                        "power_density_max": 8,
                        "power_density_unit": "W/m²",
                        "color_temperature_min": 3000,
                        "color_temperature_max": 6500,
                        "color_temperature_unit": "K",
                        "cri_min": 80
                    },
                    "industrial": {
                        "illuminance_min": 300,
                        "illuminance_unit": "lux",
                        "uniformity_min": 0.4,
                        "ugr_max": 25,
                        "power_density_max": 15,
                        "power_density_unit": "W/m²",
                        "color_temperature_min": 3000,
                        "color_temperature_max": 6500,
                        "color_temperature_unit": "K",
                        "cri_min": 80
                    }
                }
            },
            "BREEAM": {
                "name": "BREEAM - Building Research Establishment Environmental Assessment Method",
                "version": "2018",
                "requirements": {
                    "office": {
                        "illuminance_min": 500,
                        "illuminance_unit": "lux",
                        "uniformity_min": 0.7,
                        "ugr_max": 19,
                        "power_density_max": 10,
                        "power_density_unit": "W/m²",
                        "color_temperature_min": 3000,
                        "color_temperature_max": 6500,
                        "color_temperature_unit": "K",
                        "cri_min": 80
                    }
                }
            }
        }
    
    def _save_standards_database(self, database: Dict[str, Any]):
        """Save standards database to file"""
        db_path = Path(self.config.standards_db_path)
        db_path.parent.mkdir(exist_ok=True)
        
        try:
            with open(db_path, 'w', encoding='utf-8') as f:
                json.dump(database, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save standards database: {e}")
    
    def process_standards_document(self, pdf_path: Union[str, Path]) -> StandardsDocument:
        """
        Process a standards document PDF
        
        Args:
            pdf_path: Path to standards PDF
            
        Returns:
            Processed StandardsDocument
        """
        pdf_path = Path(pdf_path)
        logger.info(f"Processing standards document: {pdf_path}")
        
        # Extract content from PDF
        extraction_result = self.pdf_extractor.extract_from_pdf(pdf_path)
        
        # Extract tables
        tables = self.table_extractor.extract_tables_from_pdf(pdf_path)
        table_dataframes = [table.dataframe for table in tables]
        
        # Identify standard type
        standard_type = self._identify_standard_type(extraction_result.text, pdf_path.name)
        
        # Extract requirements
        requirements = self._extract_requirements(extraction_result.text, standard_type)
        
        # Create standards document
        standards_doc = StandardsDocument(
            name=pdf_path.stem,
            standard_type=standard_type,
            version=self._extract_version(extraction_result.text),
            language=self._detect_language(extraction_result.text),
            requirements=requirements,
            tables=table_dataframes,
            text_content=extraction_result.text,
            metadata=extraction_result.metadata,
            processing_date=datetime.now()
        )
        
        # Update database
        self._update_standards_database(standards_doc)
        
        logger.info(f"Processed standards document: {len(requirements)} requirements found")
        return standards_doc
    
    def _identify_standard_type(self, text: str, filename: str) -> StandardType:
        """Identify the type of standard from text and filename"""
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        # Check for EN 12464-1
        if any(pattern in text_lower for pattern in ['en 12464-1', 'en12464-1', '12464-1']):
            return StandardType.EN_12464_1
        
        # Check for BREEAM
        if any(pattern in text_lower for pattern in ['breeam', 'building research establishment']):
            return StandardType.BREEAM
        
        # Check for IES
        if any(pattern in text_lower for pattern in ['ies', 'illuminating engineering society']):
            return StandardType.IES
        
        # Check for CIE
        if any(pattern in text_lower for pattern in ['cie', 'commission internationale']):
            return StandardType.CIE
        
        # Check for ISO 8995
        if any(pattern in text_lower for pattern in ['iso 8995', 'iso8995', '8995']):
            return StandardType.ISO_8995
        
        # Default to custom
        return StandardType.CUSTOM
    
    def _extract_version(self, text: str) -> str:
        """Extract version information from text"""
        version_patterns = [
            r'version\s+(\d+(?:\.\d+)*)',
            r'v(\d+(?:\.\d+)*)',
            r'(\d{4})',  # Year
            r'edition\s+(\d+)',
        ]
        
        for pattern in version_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "Unknown"
    
    def _detect_language(self, text: str) -> str:
        """Detect language of the text"""
        # Simple language detection based on common words
        text_lower = text.lower()
        
        english_words = ['the', 'and', 'or', 'of', 'in', 'to', 'for', 'with', 'by']
        german_words = ['der', 'die', 'das', 'und', 'oder', 'von', 'in', 'zu', 'für']
        french_words = ['le', 'la', 'les', 'et', 'ou', 'de', 'dans', 'pour', 'avec']
        
        english_count = sum(1 for word in english_words if word in text_lower)
        german_count = sum(1 for word in german_words if word in text_lower)
        french_count = sum(1 for word in french_words if word in text_lower)
        
        if english_count > german_count and english_count > french_count:
            return "en"
        elif german_count > french_count:
            return "de"
        elif french_count > 0:
            return "fr"
        else:
            return "en"  # Default to English
    
    def _extract_requirements(self, text: str, standard_type: StandardType) -> List[LightingRequirement]:
        """Extract lighting requirements from text"""
        requirements = []
        
        # Extract illuminance requirements
        illuminance_reqs = self._extract_parameter_requirements(text, 'illuminance', 'lux')
        requirements.extend(illuminance_reqs)
        
        # Extract uniformity requirements
        uniformity_reqs = self._extract_parameter_requirements(text, 'uniformity', '')
        requirements.extend(uniformity_reqs)
        
        # Extract UGR requirements
        ugr_reqs = self._extract_parameter_requirements(text, 'ugr', '')
        requirements.extend(ugr_reqs)
        
        # Extract power density requirements
        power_reqs = self._extract_parameter_requirements(text, 'power_density', 'W/m²')
        requirements.extend(power_reqs)
        
        # Extract color temperature requirements
        color_temp_reqs = self._extract_parameter_requirements(text, 'color_temperature', 'K')
        requirements.extend(color_temp_reqs)
        
        # Extract CRI requirements
        cri_reqs = self._extract_parameter_requirements(text, 'cri', '')
        requirements.extend(cri_reqs)
        
        return requirements
    
    def _extract_parameter_requirements(self, text: str, parameter: str, unit: str) -> List[LightingRequirement]:
        """Extract requirements for a specific parameter"""
        requirements = []
        
        if parameter not in self.patterns:
            return requirements
        
        for pattern in self.patterns[parameter]:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                value = float(match.group(1))
                
                # Determine room type from context
                room_type = self._determine_room_type_from_context(text, match.start(), match.end())
                
                # Determine condition (min, max, avg)
                condition = self._determine_condition_from_context(text, match.start(), match.end())
                
                requirement = LightingRequirement(
                    parameter=parameter,
                    value=value,
                    unit=unit,
                    condition=condition,
                    room_type=room_type,
                    standard=StandardType.EN_12464_1,  # Default, should be determined from context
                    description=f"{parameter} requirement for {room_type.value}"
                )
                
                requirements.append(requirement)
        
        return requirements
    
    def _determine_room_type_from_context(self, text: str, start: int, end: int) -> RoomType:
        """Determine room type from context around the match"""
        context_start = max(0, start - 200)
        context_end = min(len(text), end + 200)
        context = text[context_start:context_end].lower()
        
        for room_type, patterns in self.room_patterns.items():
            for pattern in patterns:
                if re.search(pattern, context):
                    return RoomType(room_type)
        
        return RoomType.OFFICE  # Default
    
    def _determine_condition_from_context(self, text: str, start: int, end: int) -> str:
        """Determine condition (min, max, avg) from context"""
        context_start = max(0, start - 100)
        context_end = min(len(text), end + 100)
        context = text[context_start:context_end].lower()
        
        if any(word in context for word in ['minimum', 'min', 'least']):
            return 'minimum'
        elif any(word in context for word in ['maximum', 'max', 'most']):
            return 'maximum'
        elif any(word in context for word in ['average', 'avg', 'mean']):
            return 'average'
        else:
            return 'minimum'  # Default
    
    def _update_standards_database(self, standards_doc: StandardsDocument):
        """Update the standards database with new document"""
        standard_key = standards_doc.standard_type.value
        
        if standard_key not in self.standards_database:
            self.standards_database[standard_key] = {
                "name": standards_doc.name,
                "version": standards_doc.version,
                "requirements": {}
            }
        
        # Update requirements
        for req in standards_doc.requirements:
            room_key = req.room_type.value
            if room_key not in self.standards_database[standard_key]["requirements"]:
                self.standards_database[standard_key]["requirements"][room_key] = {}
            
            param_key = f"{req.parameter}_{req.condition}"
            self.standards_database[standard_key]["requirements"][room_key][param_key] = req.value
        
        # Save updated database
        self._save_standards_database(self.standards_database)
    
    def check_compliance(self, actual_values: Dict[str, float], room_type: RoomType, 
                        standard: StandardType) -> List[ComplianceResult]:
        """
        Check compliance of actual values against standards
        
        Args:
            actual_values: Dictionary of parameter values
            room_type: Type of room/space
            standard: Standard to check against
            
        Returns:
            List of compliance results
        """
        compliance_results = []
        
        if standard.value not in self.standards_database:
            logger.warning(f"Standard {standard.value} not found in database")
            return compliance_results
        
        standard_data = self.standards_database[standard.value]
        room_key = room_type.value
        
        if room_key not in standard_data.get("requirements", {}):
            logger.warning(f"Room type {room_key} not found for standard {standard.value}")
            return compliance_results
        
        room_requirements = standard_data["requirements"][room_key]
        
        for param, actual_value in actual_values.items():
            # Check for minimum requirements
            min_key = f"{param}_minimum"
            if min_key in room_requirements:
                required_value = room_requirements[min_key]
                is_compliant = actual_value >= required_value
                compliance_percentage = (actual_value / required_value) * 100 if required_value > 0 else 0
                deviation = actual_value - required_value
                
                result = ComplianceResult(
                    parameter=param,
                    required_value=required_value,
                    actual_value=actual_value,
                    unit=self._get_parameter_unit(param),
                    is_compliant=is_compliant,
                    compliance_percentage=compliance_percentage,
                    deviation=deviation,
                    room_type=room_type,
                    standard=standard,
                    notes="Minimum requirement check"
                )
                compliance_results.append(result)
            
            # Check for maximum requirements
            max_key = f"{param}_maximum"
            if max_key in room_requirements:
                required_value = room_requirements[max_key]
                is_compliant = actual_value <= required_value
                compliance_percentage = (required_value / actual_value) * 100 if actual_value > 0 else 0
                deviation = actual_value - required_value
                
                result = ComplianceResult(
                    parameter=param,
                    required_value=required_value,
                    actual_value=actual_value,
                    unit=self._get_parameter_unit(param),
                    is_compliant=is_compliant,
                    compliance_percentage=compliance_percentage,
                    deviation=deviation,
                    room_type=room_type,
                    standard=standard,
                    notes="Maximum requirement check"
                )
                compliance_results.append(result)
        
        return compliance_results
    
    def _get_parameter_unit(self, parameter: str) -> str:
        """Get unit for a parameter"""
        units = {
            'illuminance': 'lux',
            'uniformity': '',
            'ugr': '',
            'power_density': 'W/m²',
            'color_temperature': 'K',
            'cri': ''
        }
        return units.get(parameter, '')
    
    def compare_standards(self, standard_a: StandardType, standard_b: StandardType, 
                         room_type: RoomType) -> List[StandardsComparison]:
        """
        Compare two standards for a specific room type
        
        Args:
            standard_a: First standard to compare
            standard_b: Second standard to compare
            room_type: Room type to compare for
            
        Returns:
            List of comparisons
        """
        comparisons = []
        
        if (standard_a.value not in self.standards_database or 
            standard_b.value not in self.standards_database):
            logger.warning("One or both standards not found in database")
            return comparisons
        
        room_key = room_type.value
        reqs_a = self.standards_database[standard_a.value].get("requirements", {}).get(room_key, {})
        reqs_b = self.standards_database[standard_b.value].get("requirements", {}).get(room_key, {})
        
        # Find common parameters
        all_params = set(reqs_a.keys()) | set(reqs_b.keys())
        
        for param in all_params:
            if param in reqs_a and param in reqs_b:
                value_a = reqs_a[param]
                value_b = reqs_b[param]
                
                difference = value_a - value_b
                difference_percentage = (difference / value_b) * 100 if value_b != 0 else 0
                
                # Determine which is more strict
                if 'minimum' in param:
                    more_strict = standard_a if value_a > value_b else standard_b
                elif 'maximum' in param:
                    more_strict = standard_a if value_a < value_b else standard_b
                else:
                    more_strict = standard_a  # Default
                
                comparison = StandardsComparison(
                    standard_a=standard_a,
                    standard_b=standard_b,
                    room_type=room_type,
                    parameter=param,
                    value_a=value_a,
                    value_b=value_b,
                    difference=difference,
                    difference_percentage=difference_percentage,
                    more_strict=more_strict,
                    harmonization_recommendation=self._generate_harmonization_recommendation(
                        param, value_a, value_b, more_strict
                    )
                )
                comparisons.append(comparison)
        
        return comparisons
    
    def _generate_harmonization_recommendation(self, param: str, value_a: float, 
                                             value_b: float, more_strict: StandardType) -> str:
        """Generate harmonization recommendation"""
        if abs(value_a - value_b) < 0.01:  # Values are essentially the same
            return "Values are harmonized"
        
        if 'minimum' in param:
            if more_strict == StandardType.EN_12464_1:
                return f"Consider adopting EN 12464-1 value ({value_a}) for better lighting quality"
            else:
                return f"Consider adopting {more_strict.value} value ({value_b}) for better lighting quality"
        elif 'maximum' in param:
            if more_strict == StandardType.EN_12464_1:
                return f"Consider adopting EN 12464-1 value ({value_a}) for better energy efficiency"
            else:
                return f"Consider adopting {more_strict.value} value ({value_b}) for better energy efficiency"
        else:
            return "Consider harmonizing values for consistency"
    
    def get_standards_summary(self) -> Dict[str, Any]:
        """Get summary of all standards in database"""
        summary = {
            "total_standards": len(self.standards_database),
            "standards": {}
        }
        
        for standard_key, standard_data in self.standards_database.items():
            summary["standards"][standard_key] = {
                "name": standard_data.get("name", "Unknown"),
                "version": standard_data.get("version", "Unknown"),
                "room_types": list(standard_data.get("requirements", {}).keys()),
                "total_requirements": sum(
                    len(room_reqs) for room_reqs in standard_data.get("requirements", {}).values()
                )
            }
        
        return summary
    
    def export_standards_database(self, output_path: Union[str, Path]):
        """Export standards database to file"""
        output_path = Path(output_path)
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.standards_database, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Standards database exported to: {output_path}")
    
    def import_standards_database(self, input_path: Union[str, Path]):
        """Import standards database from file"""
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Standards database file not found: {input_path}")
        
        with open(input_path, 'r', encoding='utf-8') as f:
            self.standards_database = json.load(f)
        
        # Save to default location
        self._save_standards_database(self.standards_database)
        
        logger.info(f"Standards database imported from: {input_path}")
    
    def get_standards_for_room_type(self, room_type: RoomType) -> Dict[str, Dict[str, Any]]:
        """Get standards requirements for a specific room type"""
        requirements = {}
        
        for standard_name, standard_data in self.standards_database.items():
            if 'requirements' in standard_data:
                # Map room type to standard's room type naming
                room_type_key = self._map_room_type_to_standard(room_type, standard_data['requirements'])
                
                if room_type_key in standard_data['requirements']:
                    requirements[standard_name] = standard_data['requirements'][room_type_key]
                else:
                    # Fallback to office if specific room type not found
                    if 'office' in standard_data['requirements']:
                        requirements[standard_name] = standard_data['requirements']['office']
        
        return requirements
    
    def _map_room_type_to_standard(self, room_type: RoomType, available_requirements: Dict[str, Any]) -> str:
        """Map RoomType enum to standard's room type naming"""
        room_type_mapping = {
            RoomType.OFFICE: ['office', 'offices', 'workplace', 'workplaces'],
            RoomType.MEETING_ROOM: ['meeting_room', 'meeting', 'conference_room', 'conference'],
            RoomType.CONFERENCE_ROOM: ['conference_room', 'conference', 'meeting_room', 'meeting'],
            RoomType.CORRIDOR: ['corridor', 'corridors', 'hallway', 'hallways', 'passage'],
            RoomType.STORAGE: ['storage', 'warehouse', 'warehouses', 'storeroom'],
            RoomType.INDUSTRIAL: ['industrial', 'factory', 'manufacturing', 'production'],
            RoomType.RETAIL: ['retail', 'shop', 'shops', 'store', 'stores', 'commercial'],
            RoomType.EDUCATIONAL: ['educational', 'school', 'classroom', 'classrooms', 'education'],
            RoomType.HEALTHCARE: ['healthcare', 'hospital', 'medical', 'clinic'],
            RoomType.RESIDENTIAL: ['residential', 'home', 'apartment', 'dwelling'],
            RoomType.OUTDOOR: ['outdoor', 'exterior', 'external', 'outside']
        }
        
        # Get possible names for this room type
        possible_names = room_type_mapping.get(room_type, [room_type.value])
        
        # Find the first matching name in available requirements
        for name in possible_names:
            if name in available_requirements:
                return name
        
        # Default fallback
        return 'office'
