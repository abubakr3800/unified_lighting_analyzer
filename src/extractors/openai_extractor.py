"""
OpenAI-Powered Intelligent PDF Data Extractor
Uses OpenAI GPT for smart extraction of detailed information from Dialux reports
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime

import openai
import pandas as pd

try:
    from ..core.config import config
    from ..extractors.pdf_extractor import PDFExtractor
except ImportError:
    from core.config import config
    from extractors.pdf_extractor import PDFExtractor

logger = logging.getLogger(__name__)

@dataclass
class CompanyInfo:
    """Company information extracted from report"""
    project_company: Optional[str] = None
    luminaire_manufacturer: Optional[str] = None
    driver_circuit_company: Optional[str] = None
    consultant_company: Optional[str] = None
    installer_company: Optional[str] = None

@dataclass
class ProjectMetadata:
    """Project metadata extracted from report"""
    project_name: Optional[str] = None
    project_location: Optional[str] = None
    project_date: Optional[str] = None
    project_type: Optional[str] = None
    building_type: Optional[str] = None
    total_area: Optional[float] = None
    total_rooms: Optional[int] = None

@dataclass
class LuminaireDetails:
    """Luminaire details extracted from report"""
    luminaire_model: Optional[str] = None
    luminaire_type: Optional[str] = None
    driver_type: Optional[str] = None
    driver_model: Optional[str] = None
    power_consumption: Optional[float] = None
    luminous_flux: Optional[float] = None
    color_temperature: Optional[int] = None
    cri: Optional[int] = None
    beam_angle: Optional[float] = None

@dataclass
class RoomDetails:
    """Detailed room information"""
    room_name: str
    room_type: str
    area: float
    illuminance_avg: Optional[float] = None
    illuminance_min: Optional[float] = None
    illuminance_max: Optional[float] = None
    uniformity: Optional[float] = None
    ugr: Optional[float] = None
    power_density: Optional[float] = None
    luminaire_count: Optional[int] = None
    luminaire_spacing: Optional[float] = None

@dataclass
class IntelligentExtractionResult:
    """Result of intelligent extraction using OpenAI"""
    project_metadata: ProjectMetadata
    company_info: CompanyInfo
    luminaire_details: List[LuminaireDetails]
    room_details: List[RoomDetails]
    raw_text: str
    extraction_confidence: float
    processing_time: float
    openai_model_used: str

class OpenAIIntelligentExtractor:
    """OpenAI-powered intelligent extractor for Dialux reports"""
    
    def __init__(self, api_key: str = None):
        """Initialize the OpenAI extractor"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        # Set up OpenAI client
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Initialize PDF extractor for getting raw text
        self.pdf_extractor = PDFExtractor()
        
        logger.info("OpenAI Intelligent Extractor initialized")
    
    def extract_intelligent_data(self, pdf_path: Union[str, Path]) -> IntelligentExtractionResult:
        """Extract intelligent data from PDF using OpenAI"""
        start_time = datetime.now()
        pdf_path = Path(pdf_path)
        
        logger.info(f"Starting intelligent extraction from: {pdf_path}")
        
        try:
            # First, extract raw text from PDF
            logger.info("Extracting raw text from PDF...")
            pdf_result = self.pdf_extractor.extract_from_pdf(pdf_path)
            raw_text = pdf_result.text
            
            if not raw_text or len(raw_text.strip()) < 100:
                logger.warning("Insufficient text extracted from PDF")
                raw_text = "No readable text found in PDF"
            
            # Use OpenAI to extract structured data
            logger.info("Using OpenAI for intelligent data extraction...")
            extracted_data = self._extract_with_openai(raw_text)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Intelligent extraction completed in {processing_time:.2f}s")
            
            return IntelligentExtractionResult(
                project_metadata=extracted_data.get('project_metadata', ProjectMetadata()),
                company_info=extracted_data.get('company_info', CompanyInfo()),
                luminaire_details=extracted_data.get('luminaire_details', []),
                room_details=extracted_data.get('room_details', []),
                raw_text=raw_text,
                extraction_confidence=extracted_data.get('confidence', 0.8),
                processing_time=processing_time,
                openai_model_used="gpt-4"
            )
            
        except Exception as e:
            logger.error(f"Intelligent extraction failed: {e}")
            raise
    
    def _extract_with_openai(self, text: str) -> Dict[str, Any]:
        """Use OpenAI to extract structured data from text"""
        
        prompt = f"""
You are an expert lighting engineer analyzing a Dialux lighting report. Extract the following information from the text below and return it as a JSON object.

IMPORTANT: 
- Extract ALL numerical values (areas, illuminance, etc.) as numbers, not text
- If area is mentioned in square meters (m²), convert to float
- If illuminance is in lux, extract as float
- If uniformity is a ratio (like 0.6), extract as float
- If UGR is mentioned, extract as float
- If power density is in W/m², extract as float

Text to analyze:
{text[:8000]}  # Limit text to avoid token limits

Extract and return a JSON object with this structure:
{{
    "project_metadata": {{
        "project_name": "string or null",
        "project_location": "string or null", 
        "project_date": "string or null",
        "project_type": "string or null",
        "building_type": "string or null",
        "total_area": number or null,
        "total_rooms": number or null
    }},
    "company_info": {{
        "project_company": "string or null",
        "luminaire_manufacturer": "string or null", 
        "driver_circuit_company": "string or null",
        "consultant_company": "string or null",
        "installer_company": "string or null"
    }},
    "luminaire_details": [
        {{
            "luminaire_model": "string or null",
            "luminaire_type": "string or null",
            "driver_type": "string or null", 
            "driver_model": "string or null",
            "power_consumption": number or null,
            "luminous_flux": number or null,
            "color_temperature": number or null,
            "cri": number or null,
            "beam_angle": number or null
        }}
    ],
    "room_details": [
        {{
            "room_name": "string",
            "room_type": "string",
            "area": number,
            "illuminance_avg": number or null,
            "illuminance_min": number or null, 
            "illuminance_max": number or null,
            "uniformity": number or null,
            "ugr": number or null,
            "power_density": number or null,
            "luminaire_count": number or null,
            "luminaire_spacing": number or null
        }}
    ],
    "confidence": number between 0 and 1
}}

Focus on finding:
1. All room areas (in m²) - this is critical!
2. Illuminance values (in lux)
3. Uniformity ratios
4. UGR values
5. Power density (W/m²)
6. Company names and manufacturers
7. Driver circuit information
8. Luminaire specifications

Return ONLY the JSON object, no other text.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert lighting engineer. Extract structured data from lighting reports and return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            # Parse the response
            response_text = response.choices[0].message.content.strip()
            
            # Clean up the response (remove any markdown formatting)
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            # Parse JSON
            extracted_data = json.loads(response_text)
            
            # Convert to proper data classes
            result = {}
            
            # Project metadata
            if 'project_metadata' in extracted_data:
                pm_data = extracted_data['project_metadata']
                result['project_metadata'] = ProjectMetadata(
                    project_name=pm_data.get('project_name'),
                    project_location=pm_data.get('project_location'),
                    project_date=pm_data.get('project_date'),
                    project_type=pm_data.get('project_type'),
                    building_type=pm_data.get('building_type'),
                    total_area=pm_data.get('total_area'),
                    total_rooms=pm_data.get('total_rooms')
                )
            
            # Company info
            if 'company_info' in extracted_data:
                ci_data = extracted_data['company_info']
                result['company_info'] = CompanyInfo(
                    project_company=ci_data.get('project_company'),
                    luminaire_manufacturer=ci_data.get('luminaire_manufacturer'),
                    driver_circuit_company=ci_data.get('driver_circuit_company'),
                    consultant_company=ci_data.get('consultant_company'),
                    installer_company=ci_data.get('installer_company')
                )
            
            # Luminaire details
            result['luminaire_details'] = []
            if 'luminaire_details' in extracted_data:
                for ld_data in extracted_data['luminaire_details']:
                    result['luminaire_details'].append(LuminaireDetails(
                        luminaire_model=ld_data.get('luminaire_model'),
                        luminaire_type=ld_data.get('luminaire_type'),
                        driver_type=ld_data.get('driver_type'),
                        driver_model=ld_data.get('driver_model'),
                        power_consumption=ld_data.get('power_consumption'),
                        luminous_flux=ld_data.get('luminous_flux'),
                        color_temperature=ld_data.get('color_temperature'),
                        cri=ld_data.get('cri'),
                        beam_angle=ld_data.get('beam_angle')
                    ))
            
            # Room details
            result['room_details'] = []
            if 'room_details' in extracted_data:
                for rd_data in extracted_data['room_details']:
                    result['room_details'].append(RoomDetails(
                        room_name=rd_data.get('room_name', 'Unknown'),
                        room_type=rd_data.get('room_type', 'unknown'),
                        area=rd_data.get('area', 0.0),
                        illuminance_avg=rd_data.get('illuminance_avg'),
                        illuminance_min=rd_data.get('illuminance_min'),
                        illuminance_max=rd_data.get('illuminance_max'),
                        uniformity=rd_data.get('uniformity'),
                        ugr=rd_data.get('ugr'),
                        power_density=rd_data.get('power_density'),
                        luminaire_count=rd_data.get('luminaire_count'),
                        luminaire_spacing=rd_data.get('luminaire_spacing')
                    ))
            
            result['confidence'] = extracted_data.get('confidence', 0.8)
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response as JSON: {e}")
            logger.error(f"Response was: {response_text}")
            raise
        except Exception as e:
            logger.error(f"OpenAI extraction failed: {e}")
            raise
    
    def export_results(self, result: IntelligentExtractionResult, output_path: Path) -> Dict[str, str]:
        """Export extraction results to various formats"""
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)
        
        base_name = "intelligent_extraction"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        export_paths = {}
        
        # Export as JSON
        json_path = output_path / f"{base_name}_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(result), f, indent=2, ensure_ascii=False, default=str)
        export_paths['json'] = str(json_path)
        
        # Export as CSV (room details)
        if result.room_details:
            csv_path = output_path / f"{base_name}_rooms_{timestamp}.csv"
            room_data = []
            for room in result.room_details:
                room_data.append(asdict(room))
            
            df = pd.DataFrame(room_data)
            df.to_csv(csv_path, index=False)
            export_paths['csv'] = str(csv_path)
        
        # Export summary report
        report_path = output_path / f"{base_name}_report_{timestamp}.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("INTELLIGENT DIALUX EXTRACTION REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            # Project metadata
            f.write("PROJECT INFORMATION:\n")
            f.write(f"Project Name: {result.project_metadata.project_name or 'Not specified'}\n")
            f.write(f"Location: {result.project_metadata.project_location or 'Not specified'}\n")
            f.write(f"Date: {result.project_metadata.project_date or 'Not specified'}\n")
            f.write(f"Building Type: {result.project_metadata.building_type or 'Not specified'}\n")
            f.write(f"Total Area: {result.project_metadata.total_area or 0:.1f} m²\n")
            f.write(f"Total Rooms: {result.project_metadata.total_rooms or 0}\n\n")
            
            # Company information
            f.write("COMPANY INFORMATION:\n")
            f.write(f"Project Company: {result.company_info.project_company or 'Not specified'}\n")
            f.write(f"Luminaire Manufacturer: {result.company_info.luminaire_manufacturer or 'Not specified'}\n")
            f.write(f"Driver Circuit Company: {result.company_info.driver_circuit_company or 'Not specified'}\n")
            f.write(f"Consultant: {result.company_info.consultant_company or 'Not specified'}\n")
            f.write(f"Installer: {result.company_info.installer_company or 'Not specified'}\n\n")
            
            # Room details
            f.write("ROOM ANALYSIS:\n")
            for room in result.room_details:
                f.write(f"\nRoom: {room.room_name} ({room.room_type})\n")
                f.write(f"  Area: {room.area:.1f} m²\n")
                if room.illuminance_avg:
                    f.write(f"  Average Illuminance: {room.illuminance_avg:.0f} lux\n")
                if room.uniformity:
                    f.write(f"  Uniformity: {room.uniformity:.2f}\n")
                if room.ugr:
                    f.write(f"  UGR: {room.ugr:.1f}\n")
                if room.power_density:
                    f.write(f"  Power Density: {room.power_density:.1f} W/m²\n")
                if room.luminaire_count:
                    f.write(f"  Luminaires: {room.luminaire_count}\n")
            
            f.write(f"\nExtraction completed in {result.processing_time:.2f} seconds\n")
            f.write(f"Confidence: {result.extraction_confidence:.1%}\n")
            f.write(f"OpenAI Model: {result.openai_model_used}\n")
        
        export_paths['report'] = str(report_path)
        
        return export_paths
