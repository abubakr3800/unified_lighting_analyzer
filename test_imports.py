#!/usr/bin/env python3
"""
Test script to check imports and basic functionality
"""
import sys
import traceback

def test_imports():
    """Test all imports"""
    print("Testing imports...")
    
    try:
        print("✓ Python version:", sys.version)
        
        # Test core imports
        print("Testing core imports...")
        from src.core.config import config
        print("✓ Core config imported")
        
        # Test extractor imports
        print("Testing extractor imports...")
        from src.extractors.pdf_extractor import PDFExtractor
        print("✓ PDF extractor imported")
        
        from src.extractors.table_extractor import AdvancedTableExtractor
        print("✓ Table extractor imported")
        
        # Test standards imports
        print("Testing standards imports...")
        from src.standards.standards_processor import StandardsProcessor
        print("✓ Standards processor imported")
        
        # Test analyzer imports
        print("Testing analyzer imports...")
        from src.analyzers.dialux_analyzer import DialuxAnalyzer
        print("✓ Dialux analyzer imported")
        
        # Test web imports
        print("Testing web imports...")
        from src.web.web_interface import UnifiedWebInterface
        print("✓ Web interface imported")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import error: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic functionality"""
    print("\nTesting basic functionality...")
    
    try:
        from src.core.config import config
        print(f"✓ Config loaded: {config.project_root}")
        
        from src.extractors.pdf_extractor import PDFExtractor
        extractor = PDFExtractor()
        print("✓ PDF extractor initialized")
        
        from src.standards.standards_processor import StandardsProcessor
        processor = StandardsProcessor()
        print("✓ Standards processor initialized")
        
        print("\n🎉 Basic functionality test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Functionality error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Unified Lighting Analyzer - Import Test")
    print("=" * 50)
    
    imports_ok = test_imports()
    if imports_ok:
        functionality_ok = test_basic_functionality()
        
        if functionality_ok:
            print("\n✅ All tests passed! System is ready to use.")
            print("\nNext steps:")
            print("1. Run: py main.py web")
            print("2. Or run: py main.py status")
        else:
            print("\n⚠️ Some functionality tests failed.")
    else:
        print("\n❌ Import tests failed. Check dependencies.")
