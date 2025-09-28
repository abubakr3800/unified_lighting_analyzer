"""
Focused Fast Extractor for Dialux Reports
Extracts only essential data quickly using targeted patterns and minimal OpenAI calls
"""
import os
import re
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
class FocusedExtractionResult:
    """Focused extraction result with only essential data"""
    project_name: Optional[str] = None
    project_company: Optional[str] = None
    luminaire_manufacturer: Optional[str] = None
    driver_circuit_company: Optional[str] = None
    rooms: List[Dict[str, Any]] = None
    luminaire_details: List[Dict[str, Any]] = None
    extraction_confidence: float = 0.0
    processing_time: float = 0.0
    
    def __post_init__(self):
        if self.rooms is None:
            self.rooms = []
        if self.luminaire_details is None:
            self.luminaire_details = []

class FocusedExtractor:
    """Focused extractor for essential Dialux data"""
    
    def __init__(self, api_key: str = None):
        """Initialize the focused extractor"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        # Set up OpenAI client only if API key is available
        if self.api_key:
            openai.api_key = self.api_key
            self.client = openai.OpenAI(api_key=self.api_key)
            self.openai_available = True
        else:
            self.client = None
            self.openai_available = False
            logger.warning("OpenAI API key not provided - company extraction will be limited")
        
        # Initialize PDF extractor
        self.pdf_extractor = PDFExtractor()
        
        # Pre-compiled regex patterns for fast extraction - Enhanced for Dialux reports
        self.area_patterns = [
            # Standard area patterns
            r'area[:\s]*(\d+(?:\.\d+)?)\s*m[²2]',
            r'(\d+(?:\.\d+)?)\s*m[²2]',
            r'(\d+(?:\.\d+)?)\s*sqm',
            r'(\d+(?:\.\d+)?)\s*square\s*meters?',
            r'room[:\s]*(\d+(?:\.\d+)?)\s*m[²2]',
            r'(\d+(?:\.\d+)?)\s*m\^2',
            # Dialux specific patterns
            r'(\d+(?:\.\d+)?)\s*m\s*[²2]',
            r'(\d+(?:\.\d+)?)\s*m2',
            r'(\d+(?:\.\d+)?)\s*m\s*2',
            r'(\d+(?:\.\d+)?)\s*sq\.?\s*m',
            r'(\d+(?:\.\d+)?)\s*square\s*m',
            r'(\d+(?:\.\d+)?)\s*m\s*square',
            # Table patterns (common in Dialux reports)
            r'(\d+(?:\.\d+)?)\s*m[²2]\s*[^\d]',
            r'(\d+(?:\.\d+)?)\s*m[²2]\s*$',
            # Decimal patterns
            r'(\d+\.\d+)\s*m[²2]',
            r'(\d+\.\d+)\s*sqm',
            # Large number patterns (for big areas)
            r'(\d{2,}(?:\.\d+)?)\s*m[²2]',
            r'(\d{2,}(?:\.\d+)?)\s*sqm',
            # Additional patterns for Dialux reports
            r'(\d+(?:\.\d+)?)\s*m\s*[²2]',
            r'(\d+(?:\.\d+)?)\s*m\s*2',
            r'(\d+(?:\.\d+)?)\s*m2',
            r'(\d+(?:\.\d+)?)\s*m\^2',
            r'(\d+(?:\.\d+)?)\s*sq\.?\s*m',
            r'(\d+(?:\.\d+)?)\s*square\s*m',
            r'(\d+(?:\.\d+)?)\s*m\s*square',
            # Patterns without units (just numbers that could be areas)
            r'(\d{2,}(?:\.\d+)?)\s+(?=\d)',  # Large numbers followed by other numbers
            r'(\d+(?:\.\d+)?)\s+(?=lux|lx)',  # Numbers followed by lux
            r'(\d+(?:\.\d+)?)\s+(?=uniformity|uniform)',  # Numbers followed by uniformity
        ]
        
        self.illuminance_patterns = [
            r'illuminance[:\s]*(\d+(?:\.\d+)?)\s*lux',
            r'(\d+(?:\.\d+)?)\s*lux',
            r'lighting[:\s]*(\d+(?:\.\d+)?)\s*lux',
            r'(\d+(?:\.\d+)?)\s*lx',
            r'(\d+(?:\.\d+)?)\s*Lux',
            r'(\d+(?:\.\d+)?)\s*LUX',
            r'(\d+(?:\.\d+)?)\s*Lx'
        ]
        
        self.uniformity_patterns = [
            r'uniformity[:\s]*(\d+(?:\.\d+)?)',
            r'u[:\s]*(\d+(?:\.\d+)?)',
            r'uniform[:\s]*(\d+(?:\.\d+)?)'
        ]
        
        self.ugr_patterns = [
            r'ugr[:\s]*(\d+(?:\.\d+)?)',
            r'glare[:\s]*(\d+(?:\.\d+)?)',
            r'UGR[:\s]*(\d+(?:\.\d+)?)'
        ]
        
        # Company name patterns
        self.company_patterns = [
            r'(?i)(philips|osram|ge|ge lighting|signify|tridonic|mean well|helvar|lutron|acuity brands)',
            r'(?i)(manufacturer[:\s]*([a-zA-Z\s&]+))',
            r'(?i)(company[:\s]*([a-zA-Z\s&]+))',
            r'(?i)(project[:\s]*([a-zA-Z\s&]+))',
            r'(?i)(client[:\s]*([a-zA-Z\s&]+))'
        ]
        
        logger.info("Focused Extractor initialized")
    
    def extract_focused_data(self, pdf_path: Union[str, Path]) -> FocusedExtractionResult:
        """Extract focused data quickly"""
        start_time = datetime.now()
        pdf_path = Path(pdf_path)
        
        logger.info(f"Starting focused extraction from: {pdf_path}")
        
        try:
            # Step 1: Extract raw text quickly
            logger.info("Extracting raw text...")
            pdf_result = self.pdf_extractor.extract_from_pdf(pdf_path)
            raw_text = pdf_result.text
            
            if not raw_text or len(raw_text.strip()) < 50:
                logger.warning("Insufficient text extracted")
                raw_text = "No readable text found"
            
            # Step 2: Debug - log sample of extracted text
            logger.info(f"Sample extracted text (first 500 chars): {raw_text[:500]}")
            
            # Step 3: Fast regex extraction for numbers
            logger.info("Performing fast regex extraction...")
            regex_data = self._extract_with_regex(raw_text)
            
            # Step 4: Extract company names (with or without OpenAI)
            if self.openai_available:
                logger.info("Extracting company information with OpenAI...")
                company_data = self._extract_companies_fast(raw_text[:2000])  # Only first 2000 chars
            else:
                logger.info("Extracting company information with regex patterns...")
                company_data = self._extract_companies_regex(raw_text)
            
            # Step 5: Combine results
            result = FocusedExtractionResult(
                project_name=company_data.get('project_name'),
                project_company=company_data.get('project_company'),
                luminaire_manufacturer=company_data.get('luminaire_manufacturer'),
                driver_circuit_company=company_data.get('driver_circuit_company'),
                rooms=regex_data.get('rooms', []),
                luminaire_details=regex_data.get('luminaire_details', []),
                extraction_confidence=0.8,  # High confidence for focused extraction
                processing_time=(datetime.now() - start_time).total_seconds()
            )
            
            logger.info(f"Focused extraction completed in {result.processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Focused extraction failed: {e}")
            raise
    
    def _extract_with_regex(self, text: str) -> Dict[str, Any]:
        """Extract numerical data using enhanced regex patterns"""
        rooms = []
        luminaire_details = []
        
        logger.info(f"Extracting from text length: {len(text)} characters")
        
        # First, let's find ALL area values in the entire text
        all_area_values = []
        for pattern in self.area_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    area_val = float(match)
                    # More flexible area range - include smaller areas and larger areas
                    if 0.01 <= area_val <= 1000000:  # Very flexible area range
                        all_area_values.append(area_val)
                except (ValueError, TypeError):
                    continue
        
        logger.info(f"Found {len(all_area_values)} area values: {all_area_values[:10]}")  # Log first 10
        
        # Find ALL illuminance values
        all_illuminance_values = []
        for pattern in self.illuminance_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    illum_val = float(match)
                    if 1 <= illum_val <= 10000:  # Reasonable illuminance range
                        all_illuminance_values.append(illum_val)
                except (ValueError, TypeError):
                    continue
        
        logger.info(f"Found {len(all_illuminance_values)} illuminance values: {all_illuminance_values[:10]}")
        
        # Find ALL uniformity values
        all_uniformity_values = []
        for pattern in self.uniformity_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    uniform_val = float(match)
                    if 0.01 <= uniform_val <= 1.0:  # Reasonable uniformity range
                        all_uniformity_values.append(uniform_val)
                except (ValueError, TypeError):
                    continue
        
        # Find ALL UGR values
        all_ugr_values = []
        for pattern in self.ugr_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    ugr_val = float(match)
                    if 1 <= ugr_val <= 50:  # Reasonable UGR range
                        all_ugr_values.append(ugr_val)
                except (ValueError, TypeError):
                    continue
        
        # Now create rooms based on found data
        # Strategy 1: If we have area values, create rooms for each
        if all_area_values:
            # Remove duplicates and sort
            unique_areas = sorted(list(set(all_area_values)), reverse=True)
            logger.info(f"Creating rooms from {len(unique_areas)} unique areas")
            
            for i, area in enumerate(unique_areas[:10]):  # Max 10 rooms
                room = {
                    'room_name': f'Room {i+1}',
                    'room_type': 'office',  # Default
                    'area': area,
                    'illuminance_avg': all_illuminance_values[i] if i < len(all_illuminance_values) else None,
                    'uniformity': all_uniformity_values[i] if i < len(all_uniformity_values) else None,
                    'ugr': all_ugr_values[i] if i < len(all_ugr_values) else None,
                    'power_density': None
                }
                rooms.append(room)
        
        # Strategy 2: If we have illuminance but no areas, create rooms with estimated areas
        elif all_illuminance_values and not all_area_values:
            logger.info("No areas found, creating rooms from illuminance data")
            for i, illuminance in enumerate(all_illuminance_values[:10]):
                # Estimate area based on illuminance (higher illuminance = smaller area typically)
                estimated_area = max(10.0, 100.0 - (illuminance / 10))  # Rough estimation
                
                room = {
                    'room_name': f'Room {i+1}',
                    'room_type': 'office',
                    'area': estimated_area,
                    'illuminance_avg': illuminance,
                    'uniformity': all_uniformity_values[i] if i < len(all_uniformity_values) else None,
                    'ugr': all_ugr_values[i] if i < len(all_ugr_values) else None,
                    'power_density': None
                }
                rooms.append(room)
        
        # Strategy 3: Try to extract from table-like structures
        if not rooms:
            logger.info("Trying table-based extraction")
            # Look for table patterns (numbers in rows/columns)
            table_pattern = r'(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)'
            table_matches = re.findall(table_pattern, text)
            
            for i, match in enumerate(table_matches[:5]):  # Max 5 rooms from tables
                try:
                    # Assume first number is area, second is illuminance
                    area_val = float(match[0])
                    illum_val = float(match[1])
                    
                    if 0.1 <= area_val <= 100000 and 1 <= illum_val <= 10000:
                        room = {
                            'room_name': f'Table Room {i+1}',
                            'room_type': 'office',
                            'area': area_val,
                            'illuminance_avg': illum_val,
                            'uniformity': None,
                            'ugr': None,
                            'power_density': None
                        }
                        rooms.append(room)
                except (ValueError, TypeError):
                    continue
        
        # Strategy 4: Look for any reasonable numbers that could be areas
        if not rooms:
            logger.info("Trying to find any reasonable numbers as potential areas")
            # Look for any numbers that could be areas (2+ digits, possibly with decimals)
            number_pattern = r'(\d{2,}(?:\.\d+)?)'
            all_numbers = re.findall(number_pattern, text)
            
            potential_areas = []
            for num_str in all_numbers:
                try:
                    num_val = float(num_str)
                    # Look for numbers that could reasonably be areas
                    if 1.0 <= num_val <= 10000:  # Reasonable area range
                        potential_areas.append(num_val)
                except (ValueError, TypeError):
                    continue
            
            # Remove duplicates and sort
            unique_areas = sorted(list(set(potential_areas)), reverse=True)
            logger.info(f"Found {len(unique_areas)} potential areas: {unique_areas[:10]}")
            
            for i, area in enumerate(unique_areas[:10]):  # Max 10 rooms
                room = {
                    'room_name': f'Estimated Room {i+1}',
                    'room_type': 'office',
                    'area': area,
                    'illuminance_avg': all_illuminance_values[i] if i < len(all_illuminance_values) else None,
                    'uniformity': all_uniformity_values[i] if i < len(all_uniformity_values) else None,
                    'ugr': all_ugr_values[i] if i < len(all_ugr_values) else None,
                    'power_density': None
                }
                rooms.append(room)
        
        # Strategy 5: Last resort - create default room
        if not rooms:
            logger.warning("No data found, creating default room")
            room = {
                'room_name': 'Default Room',
                'room_type': 'office',
                'area': 1.0,  # Minimum area
                'illuminance_avg': None,
                'uniformity': None,
                'ugr': None,
                'power_density': None
            }
            rooms.append(room)
        
        logger.info(f"Created {len(rooms)} rooms")
        for room in rooms:
            logger.info(f"  - {room['room_name']}: {room['area']} m², {room['illuminance_avg']} lux")
        
        return {
            'rooms': rooms,
            'luminaire_details': luminaire_details
        }
    
    def _extract_companies_fast(self, text: str) -> Dict[str, str]:
        """Extract company information with minimal OpenAI call"""
        
        prompt = f"""
Extract ONLY company names from this lighting report text. Return a simple JSON object.

Text: {text}

Return JSON with these fields (use null if not found):
{{
    "project_name": "string or null",
    "project_company": "string or null", 
    "luminaire_manufacturer": "string or null",
    "driver_circuit_company": "string or null"
}}

Look for:
- Project/company names
- Luminaire manufacturers (like Philips, Osram, etc.)
- Driver circuit companies
- Brand names

Return ONLY the JSON, no other text.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Faster model
                messages=[
                    {"role": "system", "content": "Extract company names from text. Return JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200  # Small response
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Clean up response
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            return json.loads(response_text)
            
        except Exception as e:
            logger.warning(f"OpenAI company extraction failed: {e}")
            return {
                'project_name': None,
                'project_company': None,
                'luminaire_manufacturer': None,
                'driver_circuit_company': None
            }
    
    def _extract_companies_regex(self, text: str) -> Dict[str, str]:
        """Extract company information using regex patterns"""
        companies = []
        
        for pattern in self.company_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # Take the first non-empty group
                    company = next((m for m in match if m and m.strip()), None)
                else:
                    company = match
                
                if company and company.strip() and len(company.strip()) > 2:
                    companies.append(company.strip())
        
        # Remove duplicates and common words
        companies = list(set(companies))
        companies = [c for c in companies if c.lower() not in ['the', 'and', 'or', 'of', 'in', 'for', 'with', 'by']]
        
        # Try to identify specific company types
        luminaire_manufacturer = None
        project_company = None
        
        for company in companies:
            company_lower = company.lower()
            if any(brand in company_lower for brand in ['philips', 'osram', 'ge', 'signify', 'tridonic', 'mean well', 'helvar', 'lutron']):
                luminaire_manufacturer = company
            elif any(word in company_lower for word in ['project', 'client', 'company']):
                project_company = company
        
        return {
            'project_name': companies[0] if companies else None,
            'project_company': project_company or (companies[0] if companies else None),
            'luminaire_manufacturer': luminaire_manufacturer,
            'driver_circuit_company': None  # Hard to identify with regex alone
        }
    
    def export_results(self, result: FocusedExtractionResult, output_path: Path) -> Dict[str, str]:
        """Export focused results"""
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        export_paths = {}
        
        # Export as JSON
        json_path = output_path / f"focused_extraction_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(result), f, indent=2, ensure_ascii=False, default=str)
        export_paths['json'] = str(json_path)
        
        # Export summary report
        report_path = output_path / f"focused_report_{timestamp}.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("FOCUSED DIALUX EXTRACTION REPORT\n")
            f.write("=" * 40 + "\n\n")
            
            f.write("PROJECT INFORMATION:\n")
            f.write(f"Project Name: {result.project_name or 'Not specified'}\n")
            f.write(f"Project Company: {result.project_company or 'Not specified'}\n")
            f.write(f"Luminaire Manufacturer: {result.luminaire_manufacturer or 'Not specified'}\n")
            f.write(f"Driver Circuit Company: {result.driver_circuit_company or 'Not specified'}\n\n")
            
            f.write("ROOM ANALYSIS:\n")
            total_area = 0
            for room in result.rooms:
                f.write(f"\nRoom: {room['room_name']} ({room['room_type']})\n")
                f.write(f"  Area: {room['area']:.1f} m²\n")
                if room['illuminance_avg']:
                    f.write(f"  Illuminance: {room['illuminance_avg']:.0f} lux\n")
                if room['uniformity']:
                    f.write(f"  Uniformity: {room['uniformity']:.2f}\n")
                if room['ugr']:
                    f.write(f"  UGR: {room['ugr']:.1f}\n")
                total_area += room['area']
            
            f.write(f"\nTotal Area: {total_area:.1f} m²\n")
            f.write(f"Total Rooms: {len(result.rooms)}\n")
            f.write(f"Extraction Time: {result.processing_time:.2f} seconds\n")
            f.write(f"Confidence: {result.extraction_confidence:.1%}\n")
        
        export_paths['report'] = str(report_path)
        
        return export_paths
