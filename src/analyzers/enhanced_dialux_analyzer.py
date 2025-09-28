"""
Enhanced Dialux Analyzer with OpenAI Integration
Uses OpenAI for intelligent extraction + standards comparison
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    from ..core.config import config
    from ..extractors.openai_extractor import OpenAIIntelligentExtractor, IntelligentExtractionResult
    from ..standards.standards_processor import StandardsProcessor, RoomType, StandardType, ComplianceResult
except ImportError:
    from core.config import config
    from extractors.openai_extractor import OpenAIIntelligentExtractor, IntelligentExtractionResult
    from standards.standards_processor import StandardsProcessor, RoomType, StandardType, ComplianceResult

logger = logging.getLogger(__name__)

@dataclass
class EnhancedRoomAnalysis:
    """Enhanced room analysis with OpenAI extraction + standards compliance"""
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
    
    # Standards compliance
    compliance_results: List[ComplianceResult] = None
    
    def __post_init__(self):
        if self.compliance_results is None:
            self.compliance_results = []

@dataclass
class EnhancedDialuxReport:
    """Enhanced Dialux report with OpenAI extraction"""
    # Project metadata (from OpenAI)
    project_name: Optional[str] = None
    project_location: Optional[str] = None
    project_date: Optional[str] = None
    project_type: Optional[str] = None
    building_type: Optional[str] = None
    
    # Company information (from OpenAI)
    project_company: Optional[str] = None
    luminaire_manufacturer: Optional[str] = None
    driver_circuit_company: Optional[str] = None
    consultant_company: Optional[str] = None
    installer_company: Optional[str] = None
    
    # Luminaire details (from OpenAI)
    luminaire_details: List[Dict[str, Any]] = None
    
    # Room analysis (from OpenAI + standards)
    rooms: List[EnhancedRoomAnalysis] = None
    
    # Summary statistics
    total_rooms: int = 0
    total_area: float = 0.0
    overall_compliance_rate: float = 0.0
    data_quality_score: float = 0.0
    
    def __post_init__(self):
        if self.luminaire_details is None:
            self.luminaire_details = []
        if self.rooms is None:
            self.rooms = []

@dataclass
class EnhancedAnalysisResult:
    """Enhanced analysis result with OpenAI extraction + standards comparison"""
    report: EnhancedDialuxReport
    recommendations: List[str]
    critical_issues: List[str]
    export_paths: Dict[str, str]
    extraction_confidence: float
    processing_time: float

class EnhancedDialuxAnalyzer:
    """Enhanced Dialux analyzer with OpenAI integration"""
    
    def __init__(self, openai_api_key: str = None):
        """Initialize the enhanced analyzer"""
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required for enhanced analysis")
        
        # Initialize OpenAI extractor
        self.openai_extractor = OpenAIIntelligentExtractor(self.openai_api_key)
        
        # Initialize standards processor
        self.standards_processor = StandardsProcessor()
        
        logger.info("Enhanced Dialux Analyzer initialized with OpenAI integration")
    
    def analyze_dialux_report(self, pdf_path: Union[str, Path]) -> EnhancedAnalysisResult:
        """Analyze Dialux report using OpenAI extraction + standards comparison"""
        start_time = datetime.now()
        pdf_path = Path(pdf_path)
        
        logger.info(f"Starting enhanced Dialux analysis: {pdf_path}")
        
        try:
            # Step 1: Use OpenAI for intelligent extraction
            logger.info("Step 1: Using OpenAI for intelligent data extraction...")
            extraction_result = self.openai_extractor.extract_intelligent_data(pdf_path)
            
            # Step 2: Create enhanced report from OpenAI extraction
            logger.info("Step 2: Creating enhanced report...")
            report = self._create_enhanced_report(extraction_result)
            
            # Step 3: Perform standards compliance checking
            logger.info("Step 3: Performing standards compliance checking...")
            self._perform_compliance_checking(report)
            
            # Step 4: Generate recommendations and critical issues
            logger.info("Step 4: Generating recommendations...")
            recommendations = self._generate_recommendations(report)
            critical_issues = self._identify_critical_issues(report)
            
            # Step 5: Export results
            logger.info("Step 5: Exporting results...")
            export_paths = self._export_enhanced_results(report, pdf_path)
            
            # Calculate total processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Enhanced analysis completed in {processing_time:.2f}s")
            
            return EnhancedAnalysisResult(
                report=report,
                recommendations=recommendations,
                critical_issues=critical_issues,
                export_paths=export_paths,
                extraction_confidence=extraction_result.extraction_confidence,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Enhanced analysis failed: {e}")
            raise
    
    def _create_enhanced_report(self, extraction_result: IntelligentExtractionResult) -> EnhancedDialuxReport:
        """Create enhanced report from OpenAI extraction result"""
        
        # Create enhanced room analyses
        enhanced_rooms = []
        for room_data in extraction_result.room_details:
            enhanced_room = EnhancedRoomAnalysis(
                room_name=room_data.room_name,
                room_type=room_data.room_type,
                area=room_data.area,
                illuminance_avg=room_data.illuminance_avg,
                illuminance_min=room_data.illuminance_min,
                illuminance_max=room_data.illuminance_max,
                uniformity=room_data.uniformity,
                ugr=room_data.ugr,
                power_density=room_data.power_density,
                luminaire_count=room_data.luminaire_count,
                luminaire_spacing=room_data.luminaire_spacing
            )
            enhanced_rooms.append(enhanced_room)
        
        # Calculate summary statistics
        total_rooms = len(enhanced_rooms)
        total_area = sum(room.area for room in enhanced_rooms)
        
        # Create enhanced report
        report = EnhancedDialuxReport(
            # Project metadata
            project_name=extraction_result.project_metadata.project_name,
            project_location=extraction_result.project_metadata.project_location,
            project_date=extraction_result.project_metadata.project_date,
            project_type=extraction_result.project_metadata.project_type,
            building_type=extraction_result.project_metadata.building_type,
            
            # Company information
            project_company=extraction_result.company_info.project_company,
            luminaire_manufacturer=extraction_result.company_info.luminaire_manufacturer,
            driver_circuit_company=extraction_result.company_info.driver_circuit_company,
            consultant_company=extraction_result.company_info.consultant_company,
            installer_company=extraction_result.company_info.installer_company,
            
            # Luminaire details
            luminaire_details=[asdict(ld) for ld in extraction_result.luminaire_details],
            
            # Room analysis
            rooms=enhanced_rooms,
            
            # Summary statistics
            total_rooms=total_rooms,
            total_area=total_area,
            data_quality_score=extraction_result.extraction_confidence
        )
        
        return report
    
    def _perform_compliance_checking(self, report: EnhancedDialuxReport):
        """Perform standards compliance checking on the report"""
        
        for room in report.rooms:
            # Determine room type for standards
            room_type = self._map_room_type(room.room_type)
            
            # Get standards requirements
            standards = self.standards_processor.get_standards_for_room_type(room_type)
            
            compliance_results = []
            
            # Check illuminance compliance
            if room.illuminance_avg is not None:
                for standard_name, requirements in standards.items():
                    if 'illuminance_min' in requirements:
                        required = requirements['illuminance_min']
                        is_compliant = room.illuminance_avg >= required
                        
                        compliance_results.append(ComplianceResult(
                            standard=standard_name,
                            parameter='illuminance',
                            actual_value=room.illuminance_avg,
                            required_value=required,
                            unit='lux',
                            is_compliant=is_compliant,
                            deviation=room.illuminance_avg - required if is_compliant else required - room.illuminance_avg
                        ))
            
            # Check uniformity compliance
            if room.uniformity is not None:
                for standard_name, requirements in standards.items():
                    if 'uniformity_min' in requirements:
                        required = requirements['uniformity_min']
                        is_compliant = room.uniformity >= required
                        
                        compliance_results.append(ComplianceResult(
                            standard=standard_name,
                            parameter='uniformity',
                            actual_value=room.uniformity,
                            required_value=required,
                            unit='ratio',
                            is_compliant=is_compliant,
                            deviation=room.uniformity - required if is_compliant else required - room.uniformity
                        ))
            
            # Check UGR compliance
            if room.ugr is not None:
                for standard_name, requirements in standards.items():
                    if 'ugr_max' in requirements:
                        required = requirements['ugr_max']
                        is_compliant = room.ugr <= required
                        
                        compliance_results.append(ComplianceResult(
                            standard=standard_name,
                            parameter='ugr',
                            actual_value=room.ugr,
                            required_value=required,
                            unit='UGR',
                            is_compliant=is_compliant,
                            deviation=room.ugr - required if not is_compliant else 0
                        ))
            
            # Check power density compliance
            if room.power_density is not None:
                for standard_name, requirements in standards.items():
                    if 'power_density_max' in requirements:
                        required = requirements['power_density_max']
                        is_compliant = room.power_density <= required
                        
                        compliance_results.append(ComplianceResult(
                            standard=standard_name,
                            parameter='power_density',
                            actual_value=room.power_density,
                            required_value=required,
                            unit='W/m²',
                            is_compliant=is_compliant,
                            deviation=room.power_density - required if not is_compliant else 0
                        ))
            
            room.compliance_results = compliance_results
        
        # Calculate overall compliance rate
        total_checks = sum(len(room.compliance_results) for room in report.rooms)
        compliant_checks = sum(
            sum(1 for result in room.compliance_results if result.is_compliant)
            for room in report.rooms
        )
        
        if total_checks > 0:
            report.overall_compliance_rate = compliant_checks / total_checks
        else:
            report.overall_compliance_rate = 0.0
    
    def _map_room_type(self, room_type: str) -> RoomType:
        """Map room type string to RoomType enum"""
        room_type_lower = room_type.lower()
        
        if 'office' in room_type_lower:
            return RoomType.OFFICE
        elif 'meeting' in room_type_lower or 'conference' in room_type_lower:
            return RoomType.MEETING_ROOM
        elif 'corridor' in room_type_lower or 'hallway' in room_type_lower:
            return RoomType.CORRIDOR
        elif 'storage' in room_type_lower or 'warehouse' in room_type_lower:
            return RoomType.STORAGE
        elif 'industrial' in room_type_lower or 'factory' in room_type_lower:
            return RoomType.INDUSTRIAL
        else:
            return RoomType.OFFICE  # Default fallback
    
    def _generate_recommendations(self, report: EnhancedDialuxReport) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        for room in report.rooms:
            room_name = room.room_name
            
            # Check for non-compliant illuminance
            illuminance_results = [r for r in room.compliance_results if r.parameter == 'illuminance' and not r.is_compliant]
            if illuminance_results:
                for result in illuminance_results:
                    recommendations.append(
                        f"Increase illuminance in '{room_name}' by {result.deviation:.0f} lux "
                        f"(current: {result.actual_value:.0f} lux, required: {result.required_value:.0f} lux)"
                    )
            
            # Check for non-compliant uniformity
            uniformity_results = [r for r in room.compliance_results if r.parameter == 'uniformity' and not r.is_compliant]
            if uniformity_results:
                for result in uniformity_results:
                    recommendations.append(
                        f"Improve uniformity in '{room_name}' by {result.deviation:.2f} "
                        f"(current: {result.actual_value:.2f}, required: {result.required_value:.2f})"
                    )
            
            # Check for non-compliant UGR
            ugr_results = [r for r in room.compliance_results if r.parameter == 'ugr' and not r.is_compliant]
            if ugr_results:
                for result in ugr_results:
                    recommendations.append(
                        f"Reduce glare in '{room_name}' by {result.deviation:.1f} UGR "
                        f"(current: {result.actual_value:.1f}, max allowed: {result.required_value:.1f})"
                    )
            
            # Check for non-compliant power density
            power_results = [r for r in room.compliance_results if r.parameter == 'power_density' and not r.is_compliant]
            if power_results:
                for result in power_results:
                    recommendations.append(
                        f"Reduce power density in '{room_name}' by {result.deviation:.1f} W/m² "
                        f"(current: {result.actual_value:.1f} W/m², max allowed: {result.required_value:.1f} W/m²)"
                    )
        
        # Add general recommendations
        if report.total_area > 0:
            recommendations.append(f"Total project area: {report.total_area:.1f} m² across {report.total_rooms} rooms")
        
        if report.luminaire_manufacturer:
            recommendations.append(f"Luminaire manufacturer: {report.luminaire_manufacturer}")
        
        if report.driver_circuit_company:
            recommendations.append(f"Driver circuit company: {report.driver_circuit_company}")
        
        return recommendations
    
    def _identify_critical_issues(self, report: EnhancedDialuxReport) -> List[str]:
        """Identify critical issues in the report"""
        critical_issues = []
        
        for room in report.rooms:
            room_name = room.room_name
            
            # Check for critical illuminance issues
            illuminance_results = [r for r in room.compliance_results if r.parameter == 'illuminance' and not r.is_compliant]
            for result in illuminance_results:
                if result.actual_value < result.required_value * 0.5:
                    critical_issues.append(
                        f"CRITICAL: Illuminance in '{room_name}' is less than 50% of requirement "
                        f"({result.actual_value:.0f} lux vs {result.required_value:.0f} lux)"
                    )
            
            # Check for critical uniformity issues
            uniformity_results = [r for r in room.compliance_results if r.parameter == 'uniformity' and not r.is_compliant]
            for result in uniformity_results:
                if result.actual_value < 0.3:
                    critical_issues.append(
                        f"CRITICAL: Very poor uniformity in '{room_name}' ({result.actual_value:.2f})"
                    )
            
            # Check for critical glare issues
            ugr_results = [r for r in room.compliance_results if r.parameter == 'ugr' and not r.is_compliant]
            for result in ugr_results:
                if result.actual_value > 25:
                    critical_issues.append(
                        f"CRITICAL: Excessive glare in '{room_name}' (UGR {result.actual_value:.1f})"
                    )
        
        return critical_issues
    
    def _export_enhanced_results(self, report: EnhancedDialuxReport, pdf_path: Path) -> Dict[str, str]:
        """Export enhanced analysis results"""
        output_dir = Path(config.dialux_output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        base_name = pdf_path.stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        export_paths = {}
        
        # Export as JSON
        json_path = output_dir / f"{base_name}_enhanced_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(report), f, indent=2, ensure_ascii=False, default=str)
        export_paths['json'] = str(json_path)
        
        # Export detailed report
        report_path = output_dir / f"{base_name}_enhanced_report_{timestamp}.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("ENHANCED DIALUX ANALYSIS REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            # Project information
            f.write("PROJECT INFORMATION:\n")
            f.write(f"Project Name: {report.project_name or 'Not specified'}\n")
            f.write(f"Location: {report.project_location or 'Not specified'}\n")
            f.write(f"Date: {report.project_date or 'Not specified'}\n")
            f.write(f"Building Type: {report.building_type or 'Not specified'}\n")
            f.write(f"Total Area: {report.total_area:.1f} m²\n")
            f.write(f"Total Rooms: {report.total_rooms}\n\n")
            
            # Company information
            f.write("COMPANY INFORMATION:\n")
            f.write(f"Project Company: {report.project_company or 'Not specified'}\n")
            f.write(f"Luminaire Manufacturer: {report.luminaire_manufacturer or 'Not specified'}\n")
            f.write(f"Driver Circuit Company: {report.driver_circuit_company or 'Not specified'}\n")
            f.write(f"Consultant: {report.consultant_company or 'Not specified'}\n")
            f.write(f"Installer: {report.installer_company or 'Not specified'}\n\n")
            
            # Room analysis with compliance
            f.write("ROOM ANALYSIS WITH COMPLIANCE:\n")
            for room in report.rooms:
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
                
                # Compliance results
                if room.compliance_results:
                    f.write("  Compliance Status:\n")
                    for result in room.compliance_results:
                        status = "✅" if result.is_compliant else "❌"
                        f.write(f"    {status} {result.parameter}: {result.actual_value} {result.unit} "
                               f"(required: {result.required_value} {result.unit})\n")
            
            f.write(f"\nOverall Compliance Rate: {report.overall_compliance_rate:.1%}\n")
            f.write(f"Data Quality Score: {report.data_quality_score:.1%}\n")
        
        export_paths['report'] = str(report_path)
        
        return export_paths
