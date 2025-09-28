#!/usr/bin/env python3
"""
Simple test for area extraction
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from extractors.focused_extractor import FocusedExtractor

def test_extraction():
    # Test text with various area formats
    test_text = """
    Room 1: 25.5 m², 500 lux
    Room 2: 15.2 m2, 300 lux  
    Room 3: 8.7 sqm, 200 lux
    Room 4: 45.3 square meters, 650 lux
    Room 5: 32.1 m², 480 lux
    Room 6: 28.9 m2, 520 lux
    
    Table data:
    100.5 m²    750 lux    0.8    18
    85.2 m²     680 lux    0.75   17
    92.3 m²     720 lux    0.82   19
    
    Some numbers: 45.3, 32.1, 28.9, 100.5, 85.2, 92.3
    """
    
    print("Testing area extraction...")
    print("Test text:")
    print(test_text)
    print("\n" + "="*50)
    
    extractor = FocusedExtractor()
    result = extractor._extract_with_regex(test_text)
    
    print(f"Found {len(result['rooms'])} rooms:")
    for i, room in enumerate(result['rooms'], 1):
        print(f"  {i}. {room['room_name']}: {room['area']} m², {room['illuminance_avg']} lux")

if __name__ == "__main__":
    test_extraction()
