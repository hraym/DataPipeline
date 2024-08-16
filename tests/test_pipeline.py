import pytest
import pandas as pd
from unittest.mock import Mock, AsyncMock, patch, ANY
from src.pipeline import WorldBankDataPipeline, get_world_bank_data
from src.api import WorldBankAPI
from src.data_processor import DataProcessor
from src.exceptions import WorldBankAPIError, DataProcessingError

@pytest.fixture
def mock_api():
    api = Mock(spec=WorldBankAPI)
    api.fetch_data = AsyncMock(return_value=[
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
    ])
    return api

@pytest.fixture
def mock_processor():
    processor = Mock(spec=DataProcessor)
    processor.process_world_bank_data.return_value = (
        pd.DataFrame({
            'GDP': [20932750000000]
        }, index=pd.MultiIndex.from_tuples([('United States', 'USA', '2020-01-01')], 
                                           names=['country_name', 'country_code', 'year'])),
        "GDP (current US$)"
    )
    return processor

@pytest.mark.asyncio
async def test_fetch_and_process_indicator(mock_api, mock_processor):
    pipeline = WorldBankDataPipeline(mock_api, mock_processor)
    df = await pipeline.fetch_and_process_indicator(Mock(), 'NY.GDP.MKTP.CD', ['USA'], 2020, 2020)
    
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert pipeline.indicator_mapping['NY.GDP.MKTP.CD'] == "GDP (current US$)"
    mock_api.fetch_data.assert_called_once_with(ANY, 'NY.GDP.MKTP.CD', ['USA'], 2020, 2020)
    mock_processor.process_world_bank_data.assert_called_once()

@pytest.mark.asyncio
async def test_fetch_and_process_indicator_error(mock_api, mock_processor):
    mock_api.fetch_data.side_effect = WorldBankAPIError("API Error")
    pipeline = WorldBankDataPipeline(mock_api, mock_processor)
    
    df = await pipeline.fetch_and_process_indicator(Mock(), 'NY.GDP.MKTP.CD', ['USA'], 2020, 2020)
    
    assert isinstance(df, pd.DataFrame)
    assert df.empty

@pytest.mark.asyncio
async def test_fetch_all_indicators(mock_api, mock_processor):
    pipeline = WorldBankDataPipeline(mock_api, mock_processor)
    result = await pipeline.fetch_all_indicators(['NY.GDP.MKTP.CD', 'SP.POP.TOTL'], ['USA', 'CHN'], 2020, 2020)
    
    assert isinstance(result, dict)
    assert len(result) == 2
    assert 'NY.GDP.MKTP.CD' in result
    assert 'SP.POP.TOTL' in result
    assert mock_api.fetch_data.call_count == 2
    assert mock_processor.process_world_bank_data.call_count == 2

@pytest.mark.asyncio
async def test_get_world_bank_data():
    with patch('src.pipeline.WorldBankAPI') as mock_api_class, \
         patch('src.pipeline.DataProcessor') as mock_processor_class, \
         patch('src.pipeline.WorldBankDataPipeline.fetch_all_indicators') as mock_fetch_all:
        
        mock_api = mock_api_class.return_value
        mock_processor = mock_processor_class.return_value
        
        mock_df = pd.DataFrame({'data': [1, 2, 3]})
        mock_fetch_all.return_value = {
            'NY.GDP.MKTP.CD': mock_df,
            'SP.POP.TOTL': mock_df
        }
        
        results, indicator_mapping = await get_world_bank_data(['NY.GDP.MKTP.CD', 'SP.POP.TOTL'], ['USA', 'CHN'], 2020, 2020)
        
        assert isinstance(results, dict)
        assert len(results) == 2
        assert 'NY.GDP.MKTP.CD' in results
        assert 'SP.POP.TOTL' in results
        assert isinstance(indicator_mapping, dict)
        mock_fetch_all.assert_called_once_with(['NY.GDP.MKTP.CD', 'SP.POP.TOTL'], ['USA', 'CHN'], 2020, 2020)

@pytest.mark.asyncio
async def test_get_world_bank_data_default_end_year():
    with patch('src.pipeline.WorldBankAPI') as mock_api_class, \
         patch('src.pipeline.DataProcessor') as mock_processor_class, \
         patch('src.pipeline.WorldBankDataPipeline.fetch_all_indicators') as mock_fetch_all, \
         patch('pandas.Timestamp.now') as mock_now:
        
        mock_now.return_value.year = 2023
        mock_fetch_all.return_value = {}
        
        await get_world_bank_data(['NY.GDP.MKTP.CD'], ['USA'])
        
        mock_fetch_all.assert_called_once_with(['NY.GDP.MKTP.CD'], ['USA'], 1960, 2023)

if __name__ == '__main__':
    pytest.main()