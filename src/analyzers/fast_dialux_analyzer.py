"""
Fast Dialux Analyzer
Uses focused extraction + standards comparison for quick results
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
    from ..extractors.focused_extractor import FocusedExtractor, FocusedExtractionResult
    from ..standards.standards_processor import StandardsProcessor, RoomType, StandardType, ComplianceResult
except ImportError:
    from core.config import config
    from extractors.focused_extractor import FocusedExtractor, FocusedExtractionResult
    from standards.standards_processor import StandardsProcessor, RoomType, StandardType, ComplianceResult

logger = logging.getLogger(__name__)

@dataclass
class FastRoomAnalysis:
    """Fast room analysis with compliance"""
    room_name: str
    room_type: str
    area: float
    illuminance_avg: Optional[float] = None
    uniformity: Optional[float] = None
    ugr: Optional[float] = None
    power_density: Optional[float] = None
    compliance_results: List[ComplianceResult] = None
    
    def __post_init__(self):
        if self.compliance_results is None:
            self.compliance_results = []
    
    @property
    def name(self) -> str:
        """Alias for room_name for compatibility"""
        return self.room_name
    
    @property
    def illuminance_min(self) -> Optional[float]:
        """Alias for illuminance_avg for compatibility"""
        return self.illuminance_avg
    
    @property
    def illuminance_max(self) -> Optional[float]:
        """Alias for illuminance_avg for compatibility"""
        return self.illuminance_avg

@dataclass
class FastDialuxReport:
    """Fast Dialux report"""
    project_name: Optional[str] = None
    project_company: Optional[str] = None
    luminaire_manufacturer: Optional[str] = None
    driver_circuit_company: Optional[str] = None
    rooms: List[FastRoomAnalysis] = None
    total_rooms: int = 0
    total_area: float = 0.0
    overall_compliance_rate: float = 0.0
    data_quality_score: float = 0.0
    
    def __post_init__(self):
        if self.rooms is None:
            self.rooms = []

@dataclass
class FastAnalysisResult:
    """Fast analysis result"""
    report: FastDialuxReport
    recommendations: List[str]
    critical_issues: List[str]
    export_paths: Dict[str, str]
    extraction_confidence: float
    processing_time: float

class FastDialuxAnalyzer:
    """Fast Dialux analyzer with focused extraction"""
    
    def __init__(self, openai_api_key: str = None):
        """Initialize the fast analyzer"""
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        # Initialize focused extractor (works with or without API key)
        self.focused_extractor = FocusedExtractor(self.openai_api_key)
        
        # Initialize standards processor
        self.standards_processor = StandardsProcessor()
        
        logger.info("Fast Dialux Analyzer initialized")
    
    def analyze_dialux_report(self, pdf_path: Union[str, Path]) -> FastAnalysisResult:
        """Analyze Dialux report quickly"""
        start_time = datetime.now()
        pdf_path = Path(pdf_path)
        
        logger.info(f"Starting fast Dialux analysis: {pdf_path}")
        
        try:
            # Step 1: Fast focused extraction
            logger.info("Step 1: Fast focused extraction...")
            extraction_result = self.focused_extractor.extract_focused_data(pdf_path)
            
            # Step 2: Create fast report
            logger.info("Step 2: Creating fast report...")
            report = self._create_fast_report(extraction_result)
            
            # Step 3: Quick compliance checking
            logger.info("Step 3: Quick compliance checking...")
            self._perform_fast_compliance_checking(report)
            
            # Step 4: Generate recommendations
            logger.info("Step 4: Generating recommendations...")
            recommendations = self._generate_fast_recommendations(report)
            critical_issues = self._identify_fast_critical_issues(report)
            
            # Step 5: Export results
            logger.info("Step 5: Exporting results...")
            export_paths = self._export_fast_results(report, pdf_path)
            
            # Calculate total processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Fast analysis completed in {processing_time:.2f}s")
            
            return FastAnalysisResult(
                report=report,
                recommendations=recommendations,
                critical_issues=critical_issues,
                export_paths=export_paths,
                extraction_confidence=extraction_result.extraction_confidence,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Fast analysis failed: {e}")
            raise
    
    def _create_fast_report(self, extraction_result: FocusedExtractionResult) -> FastDialuxReport:
        """Create fast report from extraction result"""
        
        # Create fast room analyses
        fast_rooms = []
        for room_data in extraction_result.rooms:
            fast_room = FastRoomAnalysis(
                room_name=room_data['room_name'],
                room_type=room_data['room_type'],
                area=room_data['area'],
                illuminance_avg=room_data.get('illuminance_avg'),
                uniformity=room_data.get('uniformity'),
                ugr=room_data.get('ugr'),
                power_density=room_data.get('power_density')
            )
            fast_rooms.append(fast_room)
        
        # Calculate summary statistics
        total_rooms = len(fast_rooms)
        total_area = sum(room.area for room in fast_rooms)
        
        # Create fast report
        report = FastDialuxReport(
            project_name=extraction_result.project_name,
            project_company=extraction_result.project_company,
            luminaire_manufacturer=extraction_result.luminaire_manufacturer,
            driver_circuit_company=extraction_result.driver_circuit_company,
            rooms=fast_rooms,
            total_rooms=total_rooms,
            total_area=total_area,
            data_quality_score=extraction_result.extraction_confidence
        )
        
        return report
    
    def _perform_fast_compliance_checking(self, report: FastDialuxReport):
        """Perform fast compliance checking"""
        
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
    
    def _generate_fast_recommendations(self, report: FastDialuxReport) -> List[str]:
        """Generate comprehensive fast recommendations"""
        recommendations = []
        
        # ===== ILLUMINANCE RECOMMENDATIONS =====
        for room in report.rooms:
            room_name = room.room_name
            
            # Check for non-compliant illuminance
            illuminance_results = [r for r in room.compliance_results if r.parameter == 'illuminance' and not r.is_compliant]
            if illuminance_results:
                for result in illuminance_results:
                    if result.actual_value < result.required_value * 0.5:
                        recommendations.append(
                            f"🔆 CRITICAL: Increase illuminance in '{room_name}' by {result.deviation:.0f} lux "
                            f"(current: {result.actual_value:.0f} lux, required: {result.required_value:.0f} lux). "
                            f"Consider adding more luminaires or increasing luminaire output."
                        )
                    elif result.actual_value < result.required_value * 0.8:
                        recommendations.append(
                            f"🔆 HIGH PRIORITY: Increase illuminance in '{room_name}' by {result.deviation:.0f} lux "
                            f"(current: {result.actual_value:.0f} lux, required: {result.required_value:.0f} lux). "
                            f"Consider adjusting luminaire spacing or upgrading to higher output fixtures."
                        )
                    else:
                        recommendations.append(
                            f"🔆 MODERATE: Increase illuminance in '{room_name}' by {result.deviation:.0f} lux "
                            f"(current: {result.actual_value:.0f} lux, required: {result.required_value:.0f} lux). "
                            f"Minor adjustment needed - consider dimming control or fixture adjustment."
                        )
            
            # Check for excessive illuminance
            illuminance_results_high = [r for r in room.compliance_results if r.parameter == 'illuminance' and r.is_compliant and r.actual_value > r.required_value * 1.5]
            if illuminance_results_high:
                for result in illuminance_results_high:
                    recommendations.append(
                        f"🔆 ENERGY SAVING: Reduce illuminance in '{room_name}' by {result.actual_value - result.required_value:.0f} lux "
                        f"(current: {result.actual_value:.0f} lux, required: {result.required_value:.0f} lux). "
                        f"Consider dimming or reducing luminaire count for energy efficiency."
                    )
        
        # ===== UNIFORMITY RECOMMENDATIONS =====
        for room in report.rooms:
            room_name = room.room_name
            
            # Check for non-compliant uniformity
            uniformity_results = [r for r in room.compliance_results if r.parameter == 'uniformity' and not r.is_compliant]
            if uniformity_results:
                for result in uniformity_results:
                    if result.actual_value < 0.3:
                        recommendations.append(
                            f"📐 CRITICAL: Improve uniformity in '{room_name}' by {result.deviation:.2f} "
                            f"(current: {result.actual_value:.2f}, required: {result.required_value:.2f}). "
                            f"Consider reducing luminaire spacing, adding more fixtures, or using diffusers."
                        )
                    elif result.actual_value < 0.5:
                        recommendations.append(
                            f"📐 HIGH PRIORITY: Improve uniformity in '{room_name}' by {result.deviation:.2f} "
                            f"(current: {result.actual_value:.2f}, required: {result.required_value:.2f}). "
                            f"Adjust luminaire spacing or consider different light distribution patterns."
                        )
                    else:
                        recommendations.append(
                            f"📐 MODERATE: Improve uniformity in '{room_name}' by {result.deviation:.2f} "
                            f"(current: {result.actual_value:.2f}, required: {result.required_value:.2f}). "
                            f"Minor spacing adjustment or fixture repositioning recommended."
                        )
        
        # ===== GLARE CONTROL RECOMMENDATIONS =====
        for room in report.rooms:
            room_name = room.room_name
            
            # Check for non-compliant UGR
            ugr_results = [r for r in room.compliance_results if r.parameter == 'ugr' and not r.is_compliant]
            if ugr_results:
                for result in ugr_results:
                    if result.actual_value > 25:
                        recommendations.append(
                            f"👁️ CRITICAL: Reduce glare in '{room_name}' by {result.deviation:.1f} UGR "
                            f"(current: {result.actual_value:.1f}, max allowed: {result.required_value:.1f}). "
                            f"Install louvres, diffusers, or replace with low-glare luminaires."
                        )
                    elif result.actual_value > 22:
                        recommendations.append(
                            f"👁️ HIGH PRIORITY: Reduce glare in '{room_name}' by {result.deviation:.1f} UGR "
                            f"(current: {result.actual_value:.1f}, max allowed: {result.required_value:.1f}). "
                            f"Consider adding glare control accessories or adjusting mounting height."
                        )
                    else:
                        recommendations.append(
                            f"👁️ MODERATE: Reduce glare in '{room_name}' by {result.deviation:.1f} UGR "
                            f"(current: {result.actual_value:.1f}, max allowed: {result.required_value:.1f}). "
                            f"Minor adjustment to luminaire positioning or add simple glare control."
                        )
        
        # ===== POWER EFFICIENCY RECOMMENDATIONS =====
        for room in report.rooms:
            room_name = room.room_name
            
            # Check for power density compliance
            power_results = [r for r in room.compliance_results if r.parameter == 'power_density' and not r.is_compliant]
            if power_results:
                for result in power_results:
                    recommendations.append(
                        f"⚡ POWER EFFICIENCY: Reduce power density in '{room_name}' by {result.deviation:.1f} W/m² "
                        f"(current: {result.actual_value:.1f} W/m², max allowed: {result.required_value:.1f} W/m²). "
                        f"Consider LED retrofit, dimming controls, or more efficient luminaires."
                    )
            
            # Check for high power density even if compliant
            power_results_high = [r for r in room.compliance_results if r.parameter == 'power_density' and r.is_compliant and r.actual_value > r.required_value * 0.8]
            if power_results_high:
                for result in power_results_high:
                    recommendations.append(
                        f"⚡ ENERGY OPTIMIZATION: Consider reducing power density in '{room_name}' "
                        f"(current: {result.actual_value:.1f} W/m²) for better energy efficiency. "
                        f"LED technology or smart controls could provide significant savings."
                    )
        
        # ===== GENERAL PROJECT RECOMMENDATIONS =====
        if report.total_area > 0:
            recommendations.append(
                f"📊 PROJECT OVERVIEW: Total project area of {report.total_area:.1f} m² across {report.total_rooms} rooms. "
                f"Consider implementing centralized lighting control system for energy management."
            )
        
        if report.luminaire_manufacturer:
            recommendations.append(
                f"💡 LUMINAIRE INFO: Using {report.luminaire_manufacturer} luminaires. "
                f"Verify compatibility with proposed control systems and check warranty terms."
            )
        
        if report.driver_circuit_company:
            recommendations.append(
                f"⚡ DRIVER INFO: Driver circuits by {report.driver_circuit_company}. "
                f"Ensure proper dimming compatibility and consider DALI-2 or 0-10V control integration."
            )
        
        # ===== STANDARDS COMPLIANCE RECOMMENDATIONS =====
        standards_used = set()
        for room in report.rooms:
            for result in room.compliance_results:
                standards_used.add(result.standard)
        
        if standards_used:
            recommendations.append(
                f"📋 STANDARDS COMPLIANCE: Analysis performed against {', '.join(standards_used)} standards. "
                f"Ensure all recommendations align with local building codes and energy regulations."
            )
        
        # ===== MAINTENANCE RECOMMENDATIONS =====
        recommendations.append(
            f"🔧 MAINTENANCE: Implement regular lighting maintenance schedule including "
            f"lamp replacement, cleaning, and performance monitoring to maintain compliance over time."
        )
        
        # ===== SMART LIGHTING RECOMMENDATIONS =====
        recommendations.append(
            f"🤖 SMART LIGHTING: Consider implementing occupancy sensors, daylight harvesting, "
            f"and automated dimming controls to optimize energy usage and maintain compliance."
        )
        
        return recommendations
    
    def _identify_fast_critical_issues(self, report: FastDialuxReport) -> List[str]:
        """Identify comprehensive critical issues"""
        critical_issues = []
        
        for room in report.rooms:
            room_name = room.room_name
            
            # ===== CRITICAL ILLUMINANCE ISSUES =====
            illuminance_results = [r for r in room.compliance_results if r.parameter == 'illuminance' and not r.is_compliant]
            for result in illuminance_results:
                if result.actual_value < result.required_value * 0.3:
                    critical_issues.append(
                        f"🚨 SEVERE: Illuminance in '{room_name}' is critically low at {result.actual_value:.0f} lux "
                        f"(only {result.actual_value/result.required_value*100:.0f}% of required {result.required_value:.0f} lux). "
                        f"This poses safety and productivity risks - immediate action required."
                    )
                elif result.actual_value < result.required_value * 0.5:
                    critical_issues.append(
                        f"🚨 CRITICAL: Illuminance in '{room_name}' is severely inadequate at {result.actual_value:.0f} lux "
                        f"(only {result.actual_value/result.required_value*100:.0f}% of required {result.required_value:.0f} lux). "
                        f"Workplace safety and visual comfort compromised."
                    )
                elif result.actual_value < result.required_value * 0.7:
                    critical_issues.append(
                        f"⚠️ HIGH PRIORITY: Illuminance in '{room_name}' is significantly below requirement "
                        f"({result.actual_value:.0f} lux vs {result.required_value:.0f} lux). "
                        f"Visual performance may be affected."
                    )
            
            # ===== CRITICAL UNIFORMITY ISSUES =====
            uniformity_results = [r for r in room.compliance_results if r.parameter == 'uniformity' and not r.is_compliant]
            for result in uniformity_results:
                if result.actual_value < 0.2:
                    critical_issues.append(
                        f"🚨 SEVERE: Extremely poor uniformity in '{room_name}' ({result.actual_value:.2f}). "
                        f"Severe visual discomfort and potential safety hazards from extreme light/dark contrasts."
                    )
                elif result.actual_value < 0.3:
                    critical_issues.append(
                        f"🚨 CRITICAL: Very poor uniformity in '{room_name}' ({result.actual_value:.2f}). "
                        f"Significant visual discomfort and potential eye strain."
                    )
                elif result.actual_value < 0.4:
                    critical_issues.append(
                        f"⚠️ HIGH PRIORITY: Poor uniformity in '{room_name}' ({result.actual_value:.2f}). "
                        f"Visual comfort compromised - consider lighting redesign."
                    )
            
            # ===== CRITICAL GLARE ISSUES =====
            ugr_results = [r for r in room.compliance_results if r.parameter == 'ugr' and not r.is_compliant]
            for result in ugr_results:
                if result.actual_value > 30:
                    critical_issues.append(
                        f"🚨 SEVERE: Extreme glare in '{room_name}' (UGR {result.actual_value:.1f}). "
                        f"Unacceptable visual conditions - immediate glare control required."
                    )
                elif result.actual_value > 25:
                    critical_issues.append(
                        f"🚨 CRITICAL: Excessive glare in '{room_name}' (UGR {result.actual_value:.1f}). "
                        f"Severe visual discomfort and potential safety issues."
                    )
                elif result.actual_value > 22:
                    critical_issues.append(
                        f"⚠️ HIGH PRIORITY: High glare in '{room_name}' (UGR {result.actual_value:.1f}). "
                        f"Visual comfort significantly compromised."
                    )
            
            # ===== CRITICAL POWER EFFICIENCY ISSUES =====
            power_results = [r for r in room.compliance_results if r.parameter == 'power_density' and not r.is_compliant]
            for result in power_results:
                if result.actual_value > result.required_value * 1.5:
                    critical_issues.append(
                        f"🚨 ENERGY CRITICAL: Power density in '{room_name}' is {result.actual_value:.1f} W/m² "
                        f"({result.actual_value/result.required_value*100:.0f}% above limit of {result.required_value:.1f} W/m²). "
                        f"Significant energy waste and potential code violations."
                    )
                elif result.actual_value > result.required_value * 1.2:
                    critical_issues.append(
                        f"⚠️ ENERGY HIGH: Power density in '{room_name}' exceeds limit by {result.actual_value - result.required_value:.1f} W/m². "
                        f"Energy efficiency improvements needed."
                    )
        
        # ===== PROJECT-LEVEL CRITICAL ISSUES =====
        if report.overall_compliance_rate < 0.3:
            critical_issues.append(
                f"🚨 PROJECT CRITICAL: Overall compliance rate is only {report.overall_compliance_rate*100:.1f}%. "
                f"Major lighting system redesign required to meet standards."
            )
        elif report.overall_compliance_rate < 0.5:
            critical_issues.append(
                f"⚠️ PROJECT HIGH: Overall compliance rate is {report.overall_compliance_rate*100:.1f}%. "
                f"Significant improvements needed across multiple parameters."
            )
        
        # ===== DATA QUALITY CRITICAL ISSUES =====
        if hasattr(report, 'data_quality_score') and report.data_quality_score < 0.5:
            critical_issues.append(
                f"⚠️ DATA QUALITY: Analysis confidence is low ({report.data_quality_score*100:.1f}%). "
                f"Some parameters may not be accurately extracted - manual verification recommended."
            )
        
        # ===== AREA EXTRACTION CRITICAL ISSUES =====
        if report.total_area <= 1.0:
            critical_issues.append(
                f"🚨 AREA EXTRACTION: Total area appears incorrect ({report.total_area:.1f} m²). "
                f"Area extraction may have failed - manual verification of room dimensions required."
            )
        
        return critical_issues
    
    def _export_fast_results(self, report: FastDialuxReport, pdf_path: Path) -> Dict[str, str]:
        """Export fast results"""
        output_dir = Path(config.dialux_output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        base_name = pdf_path.stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        export_paths = {}
        
        # Export as JSON
        json_path = output_dir / f"{base_name}_fast_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(report), f, indent=2, ensure_ascii=False, default=str)
        export_paths['json'] = str(json_path)
        
        # Export detailed report
        report_path = output_dir / f"{base_name}_fast_report_{timestamp}.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("FAST DIALUX ANALYSIS REPORT\n")
            f.write("=" * 40 + "\n\n")
            
            # Project information
            f.write("PROJECT INFORMATION:\n")
            f.write(f"Project Name: {report.project_name or 'Not specified'}\n")
            f.write(f"Project Company: {report.project_company or 'Not specified'}\n")
            f.write(f"Luminaire Manufacturer: {report.luminaire_manufacturer or 'Not specified'}\n")
            f.write(f"Driver Circuit Company: {report.driver_circuit_company or 'Not specified'}\n")
            f.write(f"Total Area: {report.total_area:.1f} m²\n")
            f.write(f"Total Rooms: {report.total_rooms}\n\n")
            
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
