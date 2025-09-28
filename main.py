#!/usr/bin/env python3
"""
Unified Lighting Analyzer - Main Entry Point
A comprehensive system for analyzing lighting documents, standards, and Dialux reports
"""
import sys
import os
import logging
from pathlib import Path
import click
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.config import config
from src.extractors.pdf_extractor import PDFExtractor
from src.extractors.table_extractor import AdvancedTableExtractor
from src.standards.standards_processor import StandardsProcessor
from src.analyzers.dialux_analyzer import DialuxAnalyzer
from src.analyzers.enhanced_dialux_analyzer import EnhancedDialuxAnalyzer
from src.analyzers.fast_dialux_analyzer import FastDialuxAnalyzer
from src.web.web_interface import main as run_web_interface

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.logs_dir / config.log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Unified Lighting Analyzer - Comprehensive lighting document analysis system"""
    pass

@cli.command()
@click.option('--input', '-i', required=True, help='Input PDF file path')
@click.option('--output', '-o', help='Output directory (default: data/outputs)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def extract_pdf(input: str, output: Optional[str], verbose: bool):
    """Extract text and metadata from PDF files"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    input_path = Path(input)
    if not input_path.exists():
        click.echo(f"Error: Input file {input} does not exist", err=True)
        sys.exit(1)
    
    output_dir = Path(output) if output else config.outputs_dir
    output_dir.mkdir(exist_ok=True)
    
    click.echo(f"🔍 Extracting from: {input_path}")
    
    try:
        extractor = PDFExtractor()
        result = extractor.extract_from_pdf(input_path)
        
        # Save results
        output_file = output_dir / f"{input_path.stem}_extraction.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result.text)
        
        click.echo(f"✅ Extraction completed!")
        click.echo(f"📄 Text length: {len(result.text):,} characters")
        click.echo(f"📊 Tables found: {len(result.tables)}")
        click.echo(f"🖼️ Images found: {len(result.images)}")
        click.echo(f"⏱️ Processing time: {result.processing_time:.2f}s")
        click.echo(f"💾 Results saved to: {output_file}")
        
    except Exception as e:
        click.echo(f"❌ Extraction failed: {e}", err=True)
        logger.error(f"PDF extraction failed: {e}")
        sys.exit(1)

@cli.command()
@click.option('--input', '-i', required=True, help='Input PDF file path')
@click.option('--output', '-o', help='Output directory (default: data/outputs)')
@click.option('--min-score', default=0.3, help='Minimum table quality score (0.0-1.0)')
@click.option('--min-rows', default=2, help='Minimum number of rows')
@click.option('--min-cols', default=2, help='Minimum number of columns')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def extract_tables(input: str, output: Optional[str], min_score: float, 
                  min_rows: int, min_cols: int, verbose: bool):
    """Extract tables from PDF files with quality analysis"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    input_path = Path(input)
    if not input_path.exists():
        click.echo(f"Error: Input file {input} does not exist", err=True)
        sys.exit(1)
    
    output_dir = Path(output) if output else config.outputs_dir
    output_dir.mkdir(exist_ok=True)
    
    click.echo(f"🔍 Extracting tables from: {input_path}")
    click.echo(f"⚙️ Quality thresholds: score>={min_score}, rows>={min_rows}, cols>={min_cols}")
    
    try:
        extractor = AdvancedTableExtractor()
        
        # Update config
        extractor.config.min_table_score = min_score
        extractor.config.min_rows = min_rows
        extractor.config.min_cols = min_cols
        
        tables = extractor.extract_tables_from_pdf(input_path)
        
        # Export tables
        export_paths = extractor.export_tables(tables, output_dir, input_path.stem)
        
        click.echo(f"✅ Table extraction completed!")
        click.echo(f"📊 Tables extracted: {len(tables)}")
        
        if tables:
            avg_score = sum(t.quality_metrics.overall_score for t in tables) / len(tables)
            click.echo(f"📈 Average quality score: {avg_score:.2f}")
            
            high_quality = sum(1 for t in tables if t.quality_metrics.overall_score > 0.7)
            click.echo(f"⭐ High quality tables: {high_quality}")
        
        click.echo(f"💾 Results saved to: {output_dir}")
        for key, path in export_paths.items():
            click.echo(f"  📄 {key}: {path}")
        
    except Exception as e:
        click.echo(f"❌ Table extraction failed: {e}", err=True)
        logger.error(f"Table extraction failed: {e}")
        sys.exit(1)

@cli.command()
@click.option('--input', '-i', required=True, help='Input standards PDF file path')
@click.option('--output', '-o', help='Output directory (default: data/outputs)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def process_standards(input: str, output: Optional[str], verbose: bool):
    """Process lighting standards documents"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    input_path = Path(input)
    if not input_path.exists():
        click.echo(f"Error: Input file {input} does not exist", err=True)
        sys.exit(1)
    
    output_dir = Path(output) if output else config.outputs_dir
    output_dir.mkdir(exist_ok=True)
    
    click.echo(f"🔍 Processing standards document: {input_path}")
    
    try:
        processor = StandardsProcessor()
        standards_doc = processor.process_standards_document(input_path)
        
        # Save results
        output_file = output_dir / f"{input_path.stem}_standards.json"
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(standards_doc.__dict__, f, indent=2, ensure_ascii=False, default=str)
        
        click.echo(f"✅ Standards processing completed!")
        click.echo(f"📋 Standard type: {standards_doc.standard_type.value}")
        click.echo(f"📄 Version: {standards_doc.version}")
        click.echo(f"🌐 Language: {standards_doc.language}")
        click.echo(f"📊 Requirements found: {len(standards_doc.requirements)}")
        click.echo(f"📋 Tables extracted: {len(standards_doc.tables)}")
        click.echo(f"💾 Results saved to: {output_file}")
        
    except Exception as e:
        click.echo(f"❌ Standards processing failed: {e}", err=True)
        logger.error(f"Standards processing failed: {e}")
        sys.exit(1)

@cli.command()
@click.option('--input', '-i', required=True, help='Input Dialux PDF file path')
@click.option('--output', '-o', help='Output directory (default: data/outputs)')
@click.option('--standards', help='Comma-separated list of standards to check')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def analyze_dialux(input: str, output: Optional[str], standards: Optional[str], verbose: bool):
    """Analyze Dialux reports with compliance checking"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    input_path = Path(input)
    if not input_path.exists():
        click.echo(f"Error: Input file {input} does not exist", err=True)
        sys.exit(1)
    
    output_dir = Path(output) if output else config.outputs_dir
    output_dir.mkdir(exist_ok=True)
    
    click.echo(f"🔍 Analyzing Dialux report: {input_path}")
    
    if standards:
        standards_list = [s.strip() for s in standards.split(',')]
        click.echo(f"📋 Standards to check: {', '.join(standards_list)}")
    
    try:
        analyzer = DialuxAnalyzer()
        analysis_result = analyzer.analyze_dialux_report(input_path)
        
        report = analysis_result.report
        
        click.echo(f"✅ Dialux analysis completed!")
        click.echo(f"🏢 Project: {report.project_name}")
        click.echo(f"🏠 Total rooms: {report.total_rooms}")
        click.echo(f"📐 Total area: {report.total_area:.1f} m²")
        click.echo(f"✅ Overall compliance: {report.overall_compliance_rate:.1%}")
        click.echo(f"📊 Data quality: {report.data_quality_score:.1%}")
        click.echo(f"📋 Best matching standard: {report.best_matching_standard.value if report.best_matching_standard else 'N/A'}")
        
        # Room summary
        click.echo(f"\n🏠 Room Summary:")
        for room in report.rooms:
            compliance_rate = report.standards_compliance.get(room.name, 0)
            click.echo(f"  • {room.name}: {room.area:.1f} m², {compliance_rate:.1%} compliant")
        
        # Recommendations
        if analysis_result.recommendations:
            click.echo(f"\n💡 Recommendations:")
            for i, rec in enumerate(analysis_result.recommendations[:5], 1):
                click.echo(f"  {i}. {rec}")
        
        # Critical issues
        if analysis_result.critical_issues:
            click.echo(f"\n⚠️ Critical Issues:")
            for issue in analysis_result.critical_issues:
                click.echo(f"  • {issue}")
        
        click.echo(f"\n💾 Results saved to: {output_dir}")
        for key, path in analysis_result.export_paths.items():
            click.echo(f"  📄 {key}: {path}")
        
    except Exception as e:
        click.echo(f"❌ Dialux analysis failed: {e}", err=True)
        logger.error(f"Dialux analysis failed: {e}")
        sys.exit(1)

@cli.command()
@click.option('--input', '-i', required=True, help='Input Dialux PDF file path')
@click.option('--output', '-o', help='Output directory (default: data/outputs)')
@click.option('--api-key', help='OpenAI API key (or set OPENAI_API_KEY env var)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def analyze_dialux_enhanced(input: str, output: Optional[str], api_key: Optional[str], verbose: bool):
    """Analyze Dialux reports using OpenAI for intelligent extraction + standards comparison"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    input_path = Path(input)
    if not input_path.exists():
        click.echo(f"Error: Input file {input} does not exist", err=True)
        sys.exit(1)
    
    # Check for OpenAI API key
    if not api_key and not os.getenv("OPENAI_API_KEY"):
        click.echo("Error: OpenAI API key is required. Set OPENAI_API_KEY environment variable or use --api-key", err=True)
        sys.exit(1)
    
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    
    output_dir = Path(output) if output else config.outputs_dir
    output_dir.mkdir(exist_ok=True)
    
    click.echo(f"🔍 Analyzing Dialux report with OpenAI: {input_path}")
    
    try:
        analyzer = EnhancedDialuxAnalyzer(api_key)
        analysis_result = analyzer.analyze_dialux_report(input_path)
        
        report = analysis_result.report
        
        click.echo(f"✅ Enhanced Dialux analysis completed!")
        click.echo(f"🏢 Project: {report.project_name or 'Not specified'}")
        click.echo(f"📍 Location: {report.project_location or 'Not specified'}")
        click.echo(f"🏢 Company: {report.project_company or 'Not specified'}")
        click.echo(f"💡 Luminaire Manufacturer: {report.luminaire_manufacturer or 'Not specified'}")
        click.echo(f"⚡ Driver Circuit Company: {report.driver_circuit_company or 'Not specified'}")
        click.echo(f"🏠 Total rooms: {report.total_rooms}")
        click.echo(f"📐 Total area: {report.total_area:.1f} m²")
        click.echo(f"✅ Overall compliance: {report.overall_compliance_rate:.1%}")
        click.echo(f"📊 Data quality: {report.data_quality_score:.1%}")
        click.echo(f"🤖 OpenAI confidence: {analysis_result.extraction_confidence:.1%}")
        
        # Room summary with detailed info
        click.echo(f"\n🏠 Room Analysis:")
        for room in report.rooms:
            click.echo(f"  • {room.room_name} ({room.room_type}):")
            click.echo(f"    Area: {room.area:.1f} m²")
            if room.illuminance_avg:
                click.echo(f"    Illuminance: {room.illuminance_avg:.0f} lux")
            if room.uniformity:
                click.echo(f"    Uniformity: {room.uniformity:.2f}")
            if room.ugr:
                click.echo(f"    UGR: {room.ugr:.1f}")
            if room.power_density:
                click.echo(f"    Power Density: {room.power_density:.1f} W/m²")
            
            # Compliance status
            if room.compliance_results:
                compliant_count = sum(1 for r in room.compliance_results if r.is_compliant)
                total_count = len(room.compliance_results)
                click.echo(f"    Compliance: {compliant_count}/{total_count} parameters compliant")
        
        # Recommendations
        if analysis_result.recommendations:
            click.echo(f"\n💡 Recommendations:")
            for i, rec in enumerate(analysis_result.recommendations[:10], 1):
                click.echo(f"  {i}. {rec}")
        
        # Critical issues
        if analysis_result.critical_issues:
            click.echo(f"\n⚠️ Critical Issues:")
            for issue in analysis_result.critical_issues:
                click.echo(f"  • {issue}")
        
        click.echo(f"\n💾 Results saved to: {output_dir}")
        for key, path in analysis_result.export_paths.items():
            click.echo(f"  📄 {key}: {path}")
        
    except Exception as e:
        click.echo(f"❌ Enhanced Dialux analysis failed: {e}", err=True)
        logger.error(f"Enhanced Dialux analysis failed: {e}")
        sys.exit(1)

@cli.command()
@click.option('--input', '-i', required=True, help='Input Dialux PDF file path')
@click.option('--output', '-o', help='Output directory (default: data/outputs)')
@click.option('--api-key', help='OpenAI API key (or set OPENAI_API_KEY env var)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def analyze_dialux_fast(input: str, output: Optional[str], api_key: Optional[str], verbose: bool):
    """Fast Dialux analysis using focused extraction + standards comparison"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    input_path = Path(input)
    if not input_path.exists():
        click.echo(f"Error: Input file {input} does not exist", err=True)
        sys.exit(1)
    
    # Set API key if provided (optional for fast analysis)
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    
    output_dir = Path(output) if output else config.outputs_dir
    output_dir.mkdir(exist_ok=True)
    
    click.echo(f"⚡ Fast Dialux analysis: {input_path}")
    
    try:
        analyzer = FastDialuxAnalyzer(api_key)
        analysis_result = analyzer.analyze_dialux_report(input_path)
        
        report = analysis_result.report
        
        click.echo(f"✅ Fast analysis completed in {analysis_result.processing_time:.2f}s!")
        click.echo(f"🏢 Project: {report.project_name or 'Not specified'}")
        click.echo(f"🏢 Company: {report.project_company or 'Not specified'}")
        click.echo(f"💡 Luminaire Manufacturer: {report.luminaire_manufacturer or 'Not specified'}")
        click.echo(f"⚡ Driver Circuit Company: {report.driver_circuit_company or 'Not specified'}")
        click.echo(f"🏠 Total rooms: {report.total_rooms}")
        click.echo(f"📐 Total area: {report.total_area:.1f} m²")
        click.echo(f"✅ Overall compliance: {report.overall_compliance_rate:.1%}")
        click.echo(f"📊 Data quality: {report.data_quality_score:.1%}")
        
        # Room summary with detailed info
        click.echo(f"\n🏠 Room Analysis:")
        for room in report.rooms:
            click.echo(f"  • {room.room_name} ({room.room_type}):")
            click.echo(f"    Area: {room.area:.1f} m²")
            if room.illuminance_avg:
                click.echo(f"    Illuminance: {room.illuminance_avg:.0f} lux")
            if room.uniformity:
                click.echo(f"    Uniformity: {room.uniformity:.2f}")
            if room.ugr:
                click.echo(f"    UGR: {room.ugr:.1f}")
            if room.power_density:
                click.echo(f"    Power Density: {room.power_density:.1f} W/m²")
            
            # Compliance status
            if room.compliance_results:
                compliant_count = sum(1 for r in room.compliance_results if r.is_compliant)
                total_count = len(room.compliance_results)
                click.echo(f"    Compliance: {compliant_count}/{total_count} parameters compliant")
        
        # Recommendations
        if analysis_result.recommendations:
            click.echo(f"\n💡 Recommendations:")
            for i, rec in enumerate(analysis_result.recommendations[:8], 1):
                click.echo(f"  {i}. {rec}")
        
        # Critical issues
        if analysis_result.critical_issues:
            click.echo(f"\n⚠️ Critical Issues:")
            for issue in analysis_result.critical_issues:
                click.echo(f"  • {issue}")
        
        click.echo(f"\n💾 Results saved to: {output_dir}")
        for key, path in analysis_result.export_paths.items():
            click.echo(f"  📄 {key}: {path}")
        
    except Exception as e:
        click.echo(f"❌ Fast Dialux analysis failed: {e}", err=True)
        logger.error(f"Fast Dialux analysis failed: {e}")
        sys.exit(1)

@cli.command()
@click.option('--standard-a', required=True, help='First standard to compare')
@click.option('--standard-b', required=True, help='Second standard to compare')
@click.option('--room-type', required=True, help='Room type for comparison')
@click.option('--output', '-o', help='Output directory (default: data/outputs)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def compare_standards(standard_a: str, standard_b: str, room_type: str, 
                     output: Optional[str], verbose: bool):
    """Compare two lighting standards"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    output_dir = Path(output) if output else config.outputs_dir
    output_dir.mkdir(exist_ok=True)
    
    click.echo(f"⚖️ Comparing standards: {standard_a} vs {standard_b}")
    click.echo(f"🏠 Room type: {room_type}")
    
    try:
        from src.standards.standards_processor import StandardType, RoomType
        
        standard_a_enum = StandardType(standard_a)
        standard_b_enum = StandardType(standard_b)
        room_type_enum = RoomType(room_type)
        
        processor = StandardsProcessor()
        comparisons = processor.compare_standards(standard_a_enum, standard_b_enum, room_type_enum)
        
        if not comparisons:
            click.echo("⚠️ No comparable parameters found between the selected standards")
            return
        
        click.echo(f"✅ Standards comparison completed!")
        click.echo(f"📊 Comparable parameters: {len(comparisons)}")
        
        # Summary
        more_strict_a = sum(1 for c in comparisons if c.more_strict == standard_a_enum)
        more_strict_b = sum(1 for c in comparisons if c.more_strict == standard_b_enum)
        
        click.echo(f"📈 {standard_a} more strict: {more_strict_a} parameters")
        click.echo(f"📈 {standard_b} more strict: {more_strict_b} parameters")
        
        # Save results
        output_file = output_dir / f"comparison_{standard_a}_{standard_b}_{room_type}.json"
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump([c.__dict__ for c in comparisons], f, indent=2, ensure_ascii=False, default=str)
        
        click.echo(f"💾 Results saved to: {output_file}")
        
    except Exception as e:
        click.echo(f"❌ Standards comparison failed: {e}", err=True)
        logger.error(f"Standards comparison failed: {e}")
        sys.exit(1)

@cli.command()
@click.option('--host', default='localhost', help='Host to bind to')
@click.option('--port', default=8501, help='Port to bind to')
@click.option('--debug', is_flag=True, help='Enable debug mode')
def web(host: str, port: int, debug: bool):
    """Start the web interface"""
    click.echo(f"🌐 Starting web interface on {host}:{port}")
    
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Update config
        config.web.host = host
        config.web.port = port
        config.web.debug = debug
        
        # Run web interface
        run_web_interface()
        
    except Exception as e:
        click.echo(f"❌ Web interface failed to start: {e}", err=True)
        logger.error(f"Web interface failed: {e}")
        sys.exit(1)

@cli.command()
def demo():
    """Run a complete demo with sample data"""
    click.echo("🎯 Running Unified Lighting Analyzer Demo")
    click.echo("This demo will showcase all features of the system")
    
    # Check if we have sample data
    sample_dir = Path("data/samples")
    if not sample_dir.exists():
        click.echo("⚠️ No sample data found. Please add sample PDFs to data/samples/")
        return
    
    sample_files = list(sample_dir.glob("*.pdf"))
    if not sample_files:
        click.echo("⚠️ No PDF files found in data/samples/")
        return
    
    click.echo(f"📁 Found {len(sample_files)} sample files")
    
    # Demo each feature
    for sample_file in sample_files[:3]:  # Limit to 3 files for demo
        click.echo(f"\n🔍 Processing: {sample_file.name}")
        
        try:
            # PDF extraction demo
            click.echo("  📄 Extracting text...")
            extractor = PDFExtractor()
            result = extractor.extract_from_pdf(sample_file)
            click.echo(f"    ✅ Extracted {len(result.text):,} characters")
            
            # Table extraction demo
            click.echo("  📊 Extracting tables...")
            table_extractor = AdvancedTableExtractor()
            tables = table_extractor.extract_tables_from_pdf(sample_file)
            click.echo(f"    ✅ Found {len(tables)} tables")
            
            # Try Dialux analysis if it looks like a Dialux report
            if "dialux" in sample_file.name.lower() or "report" in sample_file.name.lower():
                click.echo("  🔍 Analyzing as Dialux report...")
                analyzer = DialuxAnalyzer()
                analysis_result = analyzer.analyze_dialux_report(sample_file)
                click.echo(f"    ✅ Analyzed {analysis_result.report.total_rooms} rooms")
                click.echo(f"    📊 Compliance: {analysis_result.report.overall_compliance_rate:.1%}")
            
        except Exception as e:
            click.echo(f"    ❌ Error processing {sample_file.name}: {e}")
    
    click.echo("\n🎉 Demo completed!")
    click.echo("💡 Use 'python main.py web' to start the interactive web interface")

@cli.command()
def status():
    """Show system status and configuration"""
    click.echo("📊 Unified Lighting Analyzer Status")
    click.echo("=" * 40)
    
    # Configuration
    click.echo(f"📁 Project root: {config.project_root}")
    click.echo(f"📁 Data directory: {config.data_dir}")
    click.echo(f"📁 Logs directory: {config.logs_dir}")
    click.echo(f"📁 Outputs directory: {config.outputs_dir}")
    
    # Check directories
    click.echo(f"\n📂 Directory Status:")
    for name, path in [
        ("Data", config.data_dir),
        ("Logs", config.logs_dir),
        ("Outputs", config.outputs_dir)
    ]:
        status = "✅" if path.exists() else "❌"
        click.echo(f"  {status} {name}: {path}")
    
    # Check standards database
    click.echo(f"\n📚 Standards Database:")
    try:
        processor = StandardsProcessor()
        summary = processor.get_standards_summary()
        click.echo(f"  ✅ Standards loaded: {summary['total_standards']}")
        for standard_key, standard_info in summary['standards'].items():
            click.echo(f"    • {standard_info['name']} (v{standard_info['version']})")
    except Exception as e:
        click.echo(f"  ❌ Error loading standards: {e}")
    
    # System info
    click.echo(f"\n⚙️ System Configuration:")
    click.echo(f"  Log level: {config.log_level}")
    click.echo(f"  Web host: {config.web.host}")
    click.echo(f"  Web port: {config.web.port}")
    click.echo(f"  Max file size: {config.web.max_file_size} MB")

if __name__ == "__main__":
    cli()
