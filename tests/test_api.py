import pytest
import time
import requests
from unittest.mock import Mock, patch
from src.api import WorldBankAPI
from src.exceptions import WorldBankAPIError

@pytest.fixture
def world_bank_api():
    return WorldBankAPI('https://api.worldbank.org/v2')

@pytest.fixture
def mock_response():
    mock = Mock()
    mock.json.return_value = [
        {'page': 1, 'pages': 1, 'per_page': 50, 'total': 1},
        [{'indicator': {'id': 'NY.GDP.MKTP.CD', 'value': 'GDP (current US$)'}, 'country': {'id': 'US', 'value': 'United States'}, 'countryiso3code': 'USA', 'date': '2020', 'value': 20932750000000, 'unit': '', 'obs_status': '', 'decimal': 0}]
    ]
    mock.headers = {'X-Rate-Limit-Remaining': '100'}
    return mock

def test_fetch_data_success(world_bank_api, mock_response):
    with patch('requests.Session.get', return_value=mock_response):
        data = world_bank_api.fetch_data('NY.GDP.MKTP.CD', ['USA'], 2020, 2020)
    assert len(data) == 1
    assert data[0]['countryiso3code'] == 'USA'
    assert data[0]['date'] == '2020'

def test_fetch_data_invalid_indicator(world_bank_api):
    with pytest.raises(WorldBankAPIError):
        world_bank_api.fetch_data('INVALID_INDICATOR', ['USA'], 2020, 2020)

def test_fetch_data_invalid_country(world_bank_api):
    with pytest.raises(WorldBankAPIError):
        world_bank_api.fetch_data('NY.GDP.MKTP.CD', ['INVALID_COUNTRY'], 2020, 2020)

def test_fetch_data_invalid_year_range(world_bank_api):
    with pytest.raises(WorldBankAPIError):
        world_bank_api.fetch_data('NY.GDP.MKTP.CD', ['USA'], 2020, 2019)

def test_fetch_data_connection_error(world_bank_api):
    with patch('requests.Session.get', side_effect=requests.ConnectionError):
        with pytest.raises(WorldBankAPIError):
            world_bank_api.fetch_data('NY.GDP.MKTP.CD', ['USA'], 2020, 2020)

def test_fetch_data_timeout(world_bank_api):
    with patch('requests.Session.get', side_effect=requests.Timeout):
        with pytest.raises(WorldBankAPIError):
            world_bank_api.fetch_data('NY.GDP.MKTP.CD', ['USA'], 2020, 2020)

def test_fetch_data_http_error(world_bank_api):
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.HTTPError
    with patch('requests.Session.get', return_value=mock_response):
        with pytest.raises(WorldBankAPIError):
            world_bank_api.fetch_data('NY.GDP.MKTP.CD', ['USA'], 2020, 2020)

def test_fetch_data_empty_response(world_bank_api):
    mock_response = Mock()
    mock_response.json.return_value = [{'page': 1, 'pages': 1, 'per_page': 50, 'total': 0}, []]
    with patch('requests.Session.get', return_value=mock_response):
        with pytest.raises(WorldBankAPIError):
            world_bank_api.fetch_data('NY.GDP.MKTP.CD', ['USA'], 2020, 2020)

def test_batch_fetch_data_success(world_bank_api, mock_response):
    with patch('requests.Session.get', return_value=mock_response):
        queries = [('NY.GDP.MKTP.CD', ['USA'], 2020, 2020), ('SP.POP.TOTL', ['USA'], 2020, 2020)]
        results = world_bank_api.batch_fetch_data(queries)
    assert len(results) == 2
    assert all(len(data) == 1 for data in results.values())

def test_batch_fetch_data_partial_failure(world_bank_api, mock_response):
    def mock_fetch(url, params, timeout):
        if 'NY.GDP.MKTP.CD' in url:
            return mock_response
        raise requests.HTTPError("404 Client Error: Not Found for url: https://api.worldbank.org/v2/country/USA/indicator/INVALID_INDICATOR")

    with patch('requests.Session.get', side_effect=mock_fetch):
        queries = [('NY.GDP.MKTP.CD', ['USA'], 2020, 2020), ('INVALID_INDICATOR', ['USA'], 2020, 2020)]
        results = world_bank_api.batch_fetch_data(queries)
    
    assert len(results) == 2
    assert len(results['NY.GDP.MKTP.CD']) == 1
    assert len(results['INVALID_INDICATOR']) == 0

def test_rate_limit_handling(world_bank_api):
    mock_responses = [
        Mock(headers={'X-Rate-Limit-Remaining': '2'}),
        Mock(headers={'X-Rate-Limit-Remaining': '1'}),
        Mock(headers={'X-Rate-Limit-Remaining': '100'})
    ]
    mock_responses[0].json.return_value = [
        {'page': 1, 'pages': 3, 'per_page': 1, 'total': 3},
        [{'indicator': {'id': 'NY.GDP.MKTP.CD', 'value': 'GDP (current US$)'}, 'country': {'id': 'US', 'value': 'United States'}, 'countryiso3code': 'USA', 'date': '2020', 'value': 20932750000000, 'unit': '', 'obs_status': '', 'decimal': 0}]
    ]
    mock_responses[1].json.return_value = [
        {'page': 2, 'pages': 3, 'per_page': 1, 'total': 3},
        [{'indicator': {'id': 'NY.GDP.MKTP.CD', 'value': 'GDP (current US$)'}, 'country': {'id': 'US', 'value': 'United States'}, 'countryiso3code': 'USA', 'date': '2019', 'value': 21433226000000, 'unit': '', 'obs_status': '', 'decimal': 0}]
    ]
    mock_responses[2].json.return_value = [
        {'page': 3, 'pages': 3, 'per_page': 1, 'total': 3},
        [{'indicator': {'id': 'NY.GDP.MKTP.CD', 'value': 'GDP (current US$)'}, 'country': {'id': 'US', 'value': 'United States'}, 'countryiso3code': 'USA', 'date': '2018', 'value': 20611880000000, 'unit': '', 'obs_status': '', 'decimal': 0}]
    ]

    with patch('requests.Session.get', side_effect=mock_responses):
        with patch('time.sleep') as mock_sleep:
            data = world_bank_api.fetch_data('NY.GDP.MKTP.CD', ['USA'], 2018, 2020)

    assert len(data) == 3
    assert [d['date'] for d in data] == ['2020', '2019', '2018']
    mock_sleep.assert_called_once()

def test_data_quality_check(world_bank_api, mock_response):
    mock_response.json.return_value = [
        {'page': 1, 'pages': 1, 'per_page': 50, 'total': 1},
        [{'indicator': {'id': 'NY.GDP.MKTP.CD', 'value': 'GDP (current US$)'}, 'country': {'id': 'US', 'value': 'United States'}, 'countryiso3code': 'USA', 'date': '2020', 'value': None, 'unit': '', 'obs_status': '', 'decimal': 0}]
    ]
    with patch('requests.Session.get', return_value=mock_response):
        data = world_bank_api.fetch_data('NY.GDP.MKTP.CD', ['USA'], 2020, 2020)
    assert data[0]['value'] is None

if __name__ == '__main__':
    pytest.main()