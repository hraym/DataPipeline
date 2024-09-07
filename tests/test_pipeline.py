import pytest
import pandas as pd
from unittest.mock import Mock, patch
from datetime import datetime
from src.pipeline import WorldBankDataPipeline, get_world_bank_data
from src.api import WorldBankAPI
from src.data_processor import DataProcessor
from src.database import MongoDBHandler
from src.exceptions import WorldBankAPIError, DataProcessingError

@pytest.fixture
def mock_api():
    api = Mock(spec=WorldBankAPI)
    api.batch_fetch_data.return_value = {
        'NY.GDP.MKTP.CD': [
            {
                "indicator": {"id": "NY.GDP.MKTP.CD", "value": "GDP (current US$)"},
                "country": {"id": "US", "value": "United States"},
                "countryiso3code": "USA",
                "date": "2020",
                "value": 20932750000000,
                "unit": "",
                "obs_status": "",
                "decimal": 0
            }
        ]
    }
    return api

@pytest.fixture
def mock_processor():
    processor = Mock(spec=DataProcessor)
    processor.process_world_bank_data.return_value = (
        pd.DataFrame({
            'NY.GDP.MKTP.CD': [20932750000000]
        }, index=pd.MultiIndex.from_tuples([('United States', 'USA', 2020)], 
                                           names=['country_name', 'country_code', 'year'])),
        "GDP (current US$)"
    )
    return processor

@pytest.fixture
def mock_db_handler():
    db_handler = Mock(spec=MongoDBHandler)
    db_handler.get_latest_year.return_value = 2019
    db_handler.get_missing_data_ranges.return_value = [('USA', 2020)]
    db_handler.get_indicator_data.return_value = [
        {'country_name': 'United States', 'country_code': 'USA', 'year': 2020, 'value': 20932750000000}
    ]
    return db_handler

@pytest.fixture
def pipeline(mock_api, mock_processor, mock_db_handler):
    return WorldBankDataPipeline(mock_api, mock_processor, mock_db_handler)

def test_process_indicator_data(pipeline):
    raw_data = [
        {
            "indicator": {"id": "NY.GDP.MKTP.CD", "value": "GDP (current US$)"},
            "country": {"id": "US", "value": "United States"},
            "countryiso3code": "USA",
            "date": "2020",
            "value": 20932750000000,
        }
    ]
    df = pipeline.process_indicator_data('NY.GDP.MKTP.CD', raw_data)
    
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert pipeline.indicator_mapping['NY.GDP.MKTP.CD'] == "GDP (current US$)"
    pipeline.processor.process_world_bank_data.assert_called_once_with(raw_data, 'NY.GDP.MKTP.CD')

def test_fetch_all_indicators(pipeline):
    result = pipeline.fetch_all_indicators(['NY.GDP.MKTP.CD'], ['USA'], 2020, 2020)
    
    assert isinstance(result, dict)
    assert len(result) == 1
    assert 'NY.GDP.MKTP.CD' in result
    pipeline.api.batch_fetch_data.assert_called_once()
    pipeline.processor.process_world_bank_data.assert_called_once()
    pipeline.db_handler.insert_or_update_indicator_data.assert_called_once()

def test_get_all_data(pipeline):
    result = pipeline.get_all_data(['NY.GDP.MKTP.CD'], ['USA'], 2020, 2020)
    
    assert isinstance(result, dict)
    assert len(result) == 1
    assert 'NY.GDP.MKTP.CD' in result
    assert isinstance(result['NY.GDP.MKTP.CD'], pd.DataFrame)
    pipeline.db_handler.get_indicator_data.assert_called_once_with('NY.GDP.MKTP.CD', ['USA'], 2020, 2020)

@patch('src.pipeline.WorldBankAPI')
@patch('src.pipeline.DataProcessor')
@patch('src.pipeline.MongoDBHandler')
def test_get_world_bank_data(mock_db_handler_class, mock_processor_class, mock_api_class):
    mock_api = mock_api_class.return_value
    mock_processor = mock_processor_class.return_value
    mock_db_handler = mock_db_handler_class.return_value
    
    mock_db_handler.get_indicator_data.return_value = [
        {'country_name': 'United States', 'country_code': 'USA', 'year': 2020, 'value': 20932750000000}
    ]
    
    results, indicator_mapping = get_world_bank_data(['NY.GDP.MKTP.CD'], ['USA'], 2020, 2020)
    
    assert isinstance(results, dict)
    assert len(results) == 1
    assert 'NY.GDP.MKTP.CD' in results
    assert isinstance(indicator_mapping, dict)
    mock_api_class.assert_called_once()
    mock_processor_class.assert_called_once()
    mock_db_handler_class.assert_called_once()
    mock_db_handler.close_connection.assert_called_once()

def test_get_world_bank_data_default_end_year():
    with patch('src.pipeline.WorldBankAPI') as mock_api_class, \
         patch('src.pipeline.DataProcessor') as mock_processor_class, \
         patch('src.pipeline.MongoDBHandler') as mock_db_handler_class, \
         patch('src.pipeline.datetime') as mock_datetime:
        
        mock_datetime.now.return_value.year = 2023
        mock_db_handler = mock_db_handler_class.return_value
        mock_db_handler.get_indicator_data.return_value = []
        
        get_world_bank_data(['NY.GDP.MKTP.CD'], ['USA'])
        
        mock_db_handler.get_indicator_data.assert_called_once_with('NY.GDP.MKTP.CD', ['USA'], 1960, 2023)

@patch('src.pipeline.logger')
def test_fetch_all_indicators_error_handling(mock_logger, pipeline):
    pipeline.api.batch_fetch_data.side_effect = WorldBankAPIError("API Error")
    
    result = pipeline.fetch_all_indicators(['NY.GDP.MKTP.CD'], ['USA'], 2020, 2020)
    
    assert result == {}
    mock_logger.error.assert_called_once_with("Error processing indicator NY.GDP.MKTP.CD: API Error")

@patch('src.pipeline.logger')
def test_get_all_data_error_handling(mock_logger, pipeline):
    pipeline.db_handler.get_indicator_data.side_effect = Exception("Database Error")
    
    result = pipeline.get_all_data(['NY.GDP.MKTP.CD'], ['USA'], 2020, 2020)
    
    assert result == {}
    mock_logger.error.assert_called_once_with("Error retrieving data for NY.GDP.MKTP.CD: Database Error")

if __name__ == '__main__':
    pytest.main()