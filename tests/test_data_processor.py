import pytest
import pandas as pd
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
    df = processor.process_world_bank_data(sample_data, "GDP")
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.index.names) == ['country_name', 'country_code', 'year']
    assert 'GDP' in df.columns
    assert df.loc[('United States', 'USA', '2020-01-01'), 'GDP'] == 20932750000000

def test_process_world_bank_data_empty():
    processor = DataProcessor()
    df = processor.process_world_bank_data([], "GDP")
    
    assert isinstance(df, pd.DataFrame)
    assert df.empty

def test_process_world_bank_data_missing_values(sample_data):
    sample_data[0]['value'] = None
    processor = DataProcessor()
    df = processor.process_world_bank_data(sample_data, "GDP")
    
    assert pd.isna(df.loc[('United States', 'USA', '2020-01-01'), 'GDP'])

def test_process_world_bank_data_invalid_date(sample_data):
    sample_data[0]['date'] = 'Invalid'
    processor = DataProcessor()
    with pytest.raises(ValueError):
        processor.process_world_bank_data(sample_data, "GDP")