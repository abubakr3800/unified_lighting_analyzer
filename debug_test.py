#!/usr/bin/env python3
"""
Debug test to identify issues
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def debug_test():
    """Debug test step by step"""
    print("🔍 Starting debug test...")
    
    try:
        # Test 1: Basic imports
        print("1. Testing imports...")
        from src.extractors.pdf_extractor import PDFExtractor
        print("   ✓ PDFExtractor imported")
        
        # Test 2: File existence
        print("2. Checking file...")
        pdf_path = Path("../gpt/Report.pdf")
        print(f"   Path: {pdf_path}")
        print(f"   Exists: {pdf_path.exists()}")
        print(f"   Absolute: {pdf_path.resolve()}")
        
        if not pdf_path.exists():
            print("   ❌ File not found!")
            return False
        
        # Test 3: PDF extraction
        print("3. Testing PDF extraction...")
        extractor = PDFExtractor()
        print("   ✓ Extractor created")
        
        result = extractor.extract_from_pdf(pdf_path)
        print(f"   ✓ Extraction completed")
        print(f"   Text length: {len(result.text)}")
        print(f"   Tables: {len(result.tables)}")
        print(f"   Method: {result.extraction_method}")
        print(f"   Confidence: {result.confidence_score}")
        
        # Test 4: Show some text
        if result.text:
            print(f"   First 200 chars: {result.text[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🐛 Debug Test")
    print("=" * 20)
    
    success = debug_test()
    
    if success:
        print("\n✅ Debug test passed!")
    else:
        print("\n❌ Debug test failed!")
