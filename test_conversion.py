"""
Test script for data format conversion functionality
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import the conversion functions from the main app
from app import convert_new_format_to_old, detect_data_format

def create_test_new_format_data():
    """Create sample data in new format"""
    # Create sample time series
    base_time = datetime(2024, 1, 1, 12, 0, 0)
    times = [base_time + timedelta(minutes=i) for i in range(10)]
    
    # Create sample data
    data = {
        'biosignaltime': times,
        'heartratevalue': np.random.randint(60, 100, 10),
        'respirationratevalue': np.random.randint(12, 20, 10),
        'heartratevariabilityvalue': np.random.uniform(20, 80, 10),
        'relativestrokevolumevalue': np.random.uniform(50, 120, 10),
        'patient_id': ['P001'] * 10,
        'status': ['active'] * 10
    }
    
    return pd.DataFrame(data)

def create_test_old_format_data():
    """Create sample data in old format"""
    # Create sample time series
    base_time = datetime(2024, 1, 1, 12, 0, 0)
    times = [base_time + timedelta(hours=i) for i in range(5)]
    
    # Create sample data
    data = {
        'time': times,
        'heart_rate_max': np.random.randint(70, 110, 5),
        'heart_rate_variability_max': np.random.uniform(30, 90, 5),
        'respiration_rate_max': np.random.randint(14, 22, 5),
        'relative_stroke_volume_max': np.random.uniform(60, 130, 5)
    }
    
    return pd.DataFrame(data)

def test_format_detection():
    """Test the format detection function"""
    print("Testing format detection...")
    
    # Test new format detection
    new_df = create_test_new_format_data()
    format_detected = detect_data_format(new_df)
    print(f"New format data detected as: {format_detected}")
    assert format_detected == 'new', f"Expected 'new', got '{format_detected}'"
    
    # Test old format detection
    old_df = create_test_old_format_data()
    format_detected = detect_data_format(old_df)
    print(f"Old format data detected as: {format_detected}")
    assert format_detected == 'old', f"Expected 'old', got '{format_detected}'"
    
    print("✅ Format detection tests passed!")

def test_conversion():
    """Test the conversion function"""
    print("\nTesting data conversion...")
    
    # Create new format data
    new_df = create_test_new_format_data()
    print(f"Original columns: {list(new_df.columns)}")
    
    # Convert to old format
    converted_df = convert_new_format_to_old(new_df)
    print(f"Converted columns: {list(converted_df.columns)}")
    
    # Check that required columns exist
    required_columns = ['heart_rate_max', 'heart_rate_variability_max', 
                       'respiration_rate_max', 'relative_stroke_volume_max']
    
    for col in required_columns:
        assert col in converted_df.columns, f"Missing required column: {col}"
    
    # Check that time column exists
    assert 'time' in converted_df.columns, "Missing time column"
    
    # Check that non-numeric columns are preserved
    assert 'patient_id' in converted_df.columns, "Missing patient_id column"
    assert 'status' in converted_df.columns, "Missing status column"
    
    print("✅ Conversion tests passed!")

def test_data_integrity():
    """Test that data integrity is maintained during conversion"""
    print("\nTesting data integrity...")
    
    # Create new format data with known values
    base_time = datetime(2024, 1, 1, 12, 0, 0)
    times = [base_time + timedelta(minutes=i) for i in range(5)]
    
    data = {
        'biosignaltime': times,
        'heartratevalue': [70, 75, 80, 85, 90],
        'respirationratevalue': [15, 16, 17, 18, 19],
        'heartratevariabilityvalue': [30, 35, 40, 45, 50],
        'relativestrokevolumevalue': [60, 65, 70, 75, 80],
        'patient_id': ['P001'] * 5
    }
    
    new_df = pd.DataFrame(data)
    
    # Convert to old format
    converted_df = convert_new_format_to_old(new_df)
    
    # Check that aggregation worked correctly
    # Since we have one value per time, min/median/max should be the same
    assert converted_df['heart_rate_max'].iloc[0] == 70, "Max aggregation incorrect"
    assert converted_df['heart_rate_min'].iloc[0] == 70, "Min aggregation incorrect"
    assert converted_df['heart_rate_median'].iloc[0] == 70, "Median aggregation incorrect"
    
    print("✅ Data integrity tests passed!")

if __name__ == "__main__":
    print("Running conversion tests...\n")
    
    try:
        test_format_detection()
        test_conversion()
        test_data_integrity()
        print("\n🎉 All tests passed! The conversion functionality is working correctly.")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise 