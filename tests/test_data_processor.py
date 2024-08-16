import pytest
import pandas as pd
import numpy as np
from src.data_processor import DataProcessor

@pytest.fixture
def sample_data():
    return [
        {
            "indicator": {"id": "NY.GDP.MKTP.CD", "value": "GDP (current US$)"},
            "country": {"id": "US", "value": "United States"},
            "countryiso3code": "USA",
            "date": "2020",
            "value": 20932750000000,
            "unit": "",
            "obs_status": "",
            "decimal": 0
        },
        {
            "indicator": {"id": "NY.GDP.MKTP.CD", "value": "GDP (current US$)"},
            "country": {"id": "US", "value": "United States"},
            "countryiso3code": "USA",
            "date": "2019",
            "value": 21433226000000,
            "unit": "",
            "obs_status": "",
            "decimal": 0
        }
    ]

def test_process_world_bank_data_normal(sample_data):
    processor = DataProcessor()
    df, indicator_name = processor.process_world_bank_data(sample_data, "NY.GDP.MKTP.CD")
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.index.names) == ['country_name', 'country_code', 'year']
    assert df.index.get_level_values('country_name')[0] == 'United States'
    assert df.index.get_level_values('country_code')[0] == 'USA'
    assert df.index.get_level_values('year')[0] == 2020
    assert 'GDP (current US$)' in df.columns
    assert df.loc[('United States', 'USA', 2020), 'GDP (current US$)'] == 20932750000000
    assert indicator_name == "GDP (current US$)"

def test_process_world_bank_data_empty():
    processor = DataProcessor()
    df, indicator_name = processor.process_world_bank_data([], "NY.GDP.MKTP.CD")
    
    assert isinstance(df, pd.DataFrame)
    assert df.empty
    assert list(df.columns) == ['country_name', 'country_code', 'year', 'NY.GDP.MKTP.CD']
    assert indicator_name == "NY.GDP.MKTP.CD"

def test_process_world_bank_data_missing_values(sample_data):
    sample_data[0]['value'] = None
    processor = DataProcessor()
    df, _ = processor.process_world_bank_data(sample_data, "NY.GDP.MKTP.CD")
    
    assert len(df) == 2  # Both rows should be kept, with None converted to NaN
    assert pd.isna(df.loc[('United States', 'USA', 2020), 'GDP (current US$)'])
    assert not pd.isna(df.loc[('United States', 'USA', 2019), 'GDP (current US$)'])

def test_process_world_bank_data_invalid_date(sample_data):
    sample_data[0]['date'] = 'Invalid'
    processor = DataProcessor()
    df, _ = processor.process_world_bank_data(sample_data, "NY.GDP.MKTP.CD")
    assert len(df) == 1  # The row with invalid date should be dropped
    assert 2019 in df.index.get_level_values('year')

def test_process_world_bank_data_missing_indicator(sample_data):
    for item in sample_data:
        del item['indicator']
    processor = DataProcessor()
    df, indicator_name = processor.process_world_bank_data(sample_data, "NY.GDP.MKTP.CD")
    assert 'NY.GDP.MKTP.CD' in df.columns
    assert indicator_name == "NY.GDP.MKTP.CD"

def test_process_world_bank_data_missing_country(sample_data):
    for item in sample_data:
        del item['country']
    processor = DataProcessor()
    df, _ = processor.process_world_bank_data(sample_data, "NY.GDP.MKTP.CD")
    assert df.empty

def test_process_world_bank_data_non_dict_indicator(sample_data):
    for item in sample_data:
        item['indicator'] = "GDP (current US$)"
    processor = DataProcessor()
    df, indicator_name = processor.process_world_bank_data(sample_data, "NY.GDP.MKTP.CD")
    assert 'GDP (current US$)' in df.columns
    assert indicator_name == "GDP (current US$)"

def test_process_world_bank_data_non_dict_country(sample_data):
    for item in sample_data:
        item['country'] = "United States"
    processor = DataProcessor()
    df, _ = processor.process_world_bank_data(sample_data, "NY.GDP.MKTP.CD")
    assert 'United States' in df.index.get_level_values('country_name')

def test_process_world_bank_data_multiple_countries(sample_data):
    sample_data.append({
        "indicator": {"id": "NY.GDP.MKTP.CD", "value": "GDP (current US$)"},
        "country": {"id": "CA", "value": "Canada"},
        "countryiso3code": "CAN",
        "date": "2020",
        "value": 1643408000000,
        "unit": "",
        "obs_status": "",
        "decimal": 0
    })
    processor = DataProcessor()
    df, _ = processor.process_world_bank_data(sample_data, "NY.GDP.MKTP.CD")
    assert len(df) == 3
    assert 'Canada' in df.index.get_level_values('country_name')
    assert 'CAN' in df.index.get_level_values('country_code')

def test_process_world_bank_data_sorting(sample_data):
    processor = DataProcessor()
    df, _ = processor.process_world_bank_data(sample_data, "NY.GDP.MKTP.CD")
    assert df.index.get_level_values('year').is_monotonic_decreasing

def test_process_world_bank_data_numeric_conversion(sample_data):
    sample_data[0]['value'] = '20932750000000'  # String value
    processor = DataProcessor()
    df, _ = processor.process_world_bank_data(sample_data, "NY.GDP.MKTP.CD")
    assert isinstance(df.loc[('United States', 'USA', 2020), 'GDP (current US$)'], np.float64)
    assert df.loc[('United States', 'USA', 2020), 'GDP (current US$)'] == 20932750000000.0

def test_process_world_bank_data_error_handling(caplog):
    processor = DataProcessor()
    invalid_data = [{'invalid': 'data'}]
    df, _ = processor.process_world_bank_data(invalid_data, "NY.GDP.MKTP.CD")
    assert df.empty
    assert "No 'country' column found for indicator: NY.GDP.MKTP.CD" in caplog.text



