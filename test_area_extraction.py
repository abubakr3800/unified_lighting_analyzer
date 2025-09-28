#!/usr/bin/env python3
"""
Test script to debug area extraction issues
"""
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from extractors.focused_extractor import FocusedExtractor
from extractors.pdf_extractor import PDFExtractor

def test_area_extraction():
    """Test area extraction with sample text"""
    
    # Sample text that might be in a Dialux report
    sample_text = """
    Room 1: Office Space
    Area: 25.5 m²
    Illuminance: 500 lux
    Uniformity: 0.7
    UGR: 19
    
    Room 2: Meeting Room  
    Area: 15.2 m²
    Illuminance: 300 lux
    Uniformity: 0.8
    UGR: 16
    
    Room 3: Corridor
    Area: 8.7 m²
    Illuminance: 200 lux
    Uniformity: 0.6
    UGR: 22
    
    Table Data:
    45.3 m²    650 lux    0.75    18
    32.1 m²    480 lux    0.82    17
    28.9 m²    520 lux    0.78    19
    """
    
    print("Testing area extraction with sample text...")
    print("=" * 50)
    
    # Initialize extractor
    extractor = FocusedExtractor()
    
    # Test regex extraction
    result = extractor._extract_with_regex(sample_text)
    
    print(f"Found {len(result['rooms'])} rooms:")
    for i, room in enumerate(result['rooms'], 1):
        print(f"  Room {i}: {room['room_name']}")
        print(f"    Area: {room['area']} m²")
        print(f"    Illuminance: {room['illuminance_avg']} lux")
        print(f"    Uniformity: {room['uniformity']}")
        print(f"    UGR: {room['ugr']}")
        print()
    
    # Test with a real PDF if available
    pdf_path = Path("../gpt/Report.pdf")
    if pdf_path.exists():
        print("Testing with real PDF...")
        print("=" * 50)
        
        try:
            # First test PDF extraction
            pdf_extractor = PDFExtractor()
            pdf_result = pdf_extractor.extract_from_pdf(pdf_path)
            
            print(f"PDF extraction result:")
            print(f"  Text length: {len(pdf_result.text)} characters")
            print(f"  Tables found: {len(pdf_result.tables)}")
            print(f"  Sample text (first 500 chars):")
            print(f"  {pdf_result.text[:500]}")
            print()
            
            # Test focused extraction
            focused_result = extractor.extract_focused_data(pdf_path)
            
            print(f"Focused extraction result:")
            print(f"  Processing time: {focused_result.processing_time:.2f}s")
            print(f"  Confidence: {focused_result.extraction_confidence:.1%}")
            print(f"  Rooms found: {len(focused_result.rooms)}")
            
            for i, room in enumerate(focused_result.rooms, 1):
                print(f"    Room {i}: {room['room_name']}")
                print(f"      Area: {room['area']} m²")
                print(f"      Illuminance: {room['illuminance_avg']} lux")
                print(f"      Uniformity: {room['uniformity']}")
                print(f"      UGR: {room['ugr']}")
                print()
                
        except Exception as e:
            print(f"Error testing with real PDF: {e}")
    else:
        print(f"PDF file not found at {pdf_path}")

if __name__ == "__main__":
    test_area_extraction()
