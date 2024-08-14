import pytest
import pandas as pd
from unittest.mock import Mock, AsyncMock
from src.pipeline import WorldBankDataPipeline, get_world_bank_data
from src.api import WorldBankAPI
from src.data_processor import DataProcessor

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
    processor.process_world_bank_data.return_value = pd.DataFrame({
        'GDP': [20932750000000]
    }, index=pd.MultiIndex.from_tuples([('United States', 'USA', '2020-01-01')], 
                                       names=['country_name', 'country_code', 'year']))
    return processor

@pytest.mark.asyncio
async def test_fetch_and_process_indicator(mock_api, mock_processor):
    pipeline = WorldBankDataPipeline(mock_api, mock_processor)
    df = await pipeline.fetch_and_process_indicator(Mock(), 'NY.GDP.MKTP.CD', ['USA'], 2020, 2020)
    
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    mock_api.fetch_data.assert_called_once()
    mock_processor.process_world_bank_data.assert_called_once()

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
async def test_get_world_bank_data(monkeypatch):
    mock_pipeline = Mock(spec=WorldBankDataPipeline)
    mock_pipeline.fetch_all_indicators = AsyncMock(return_value={
        'NY.GDP.MKTP.CD': pd.DataFrame(),
        'SP.POP.TOTL': pd.DataFrame()
    })
    
    monkeypatch.setattr('src.pipeline.WorldBankDataPipeline', Mock(return_value=mock_pipeline))
    
    result = await get_world_bank_data(['NY.GDP.MKTP.CD', 'SP.POP.TOTL'], ['USA', 'CHN'], 2020, 2020)
    
    assert isinstance(result, dict)
    assert len(result) == 2
    assert 'NY.GDP.MKTP.CD' in result
    assert 'SP.POP.TOTL' in result
    mock_pipeline.fetch_all_indicators.assert_called_once()