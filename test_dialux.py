#!/usr/bin/env python3
"""
Test Dialux analysis with a specific file
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_dialux_analysis():
    """Test Dialux analysis"""
    try:
        from src.analyzers.dialux_analyzer import DialuxAnalyzer
        
        print("🔍 Testing Dialux analysis...")
        
        # Test with the Report.pdf file
        pdf_path = Path("../gpt/Report.pdf")
        if not pdf_path.exists():
            print(f"❌ File not found: {pdf_path}")
            return False
        
        print(f"📄 Analyzing: {pdf_path}")
        
        analyzer = DialuxAnalyzer()
        result = analyzer.analyze_dialux_report(pdf_path)
        
        report = result.report
        print(f"✅ Analysis completed!")
        print(f"🏢 Project: {report.project_name}")
        print(f"🏠 Total rooms: {report.total_rooms}")
        print(f"📐 Total area: {report.total_area:.1f} m²")
        print(f"✅ Overall compliance: {report.overall_compliance_rate:.1%}")
        print(f"📊 Data quality: {report.data_quality_score:.1%}")
        
        if report.rooms:
            print(f"\n🏠 Room Details:")
            for room in report.rooms:
                print(f"  • {room.name}: {room.area:.1f} m²")
                if room.illuminance_avg:
                    print(f"    Illuminance: {room.illuminance_avg:.0f} lux")
                if room.uniformity:
                    print(f"    Uniformity: {room.uniformity:.2f}")
                if room.ugr:
                    print(f"    UGR: {room.ugr:.1f}")
        
        if result.recommendations:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(result.recommendations[:3], 1):
                print(f"  {i}. {rec}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Dialux Analysis Test")
    print("=" * 30)
    
    success = test_dialux_analysis()
    
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n❌ Test failed!")
