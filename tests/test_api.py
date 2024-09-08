import pytest
import responses
from requests.exceptions import ConnectionError
from src.api import WorldBankAPI
from src.exceptions import WorldBankAPIError

@pytest.fixture(scope="module")
def world_bank_api():
    return WorldBankAPI('https://api.worldbank.org/v2')

@pytest.fixture(scope="function")
def mock_successful_response(request):
    indicator, country, start_year, end_year = request.param
    return [
        {'page': 1, 'pages': 1, 'per_page': 50, 'total': 1},
        [{
            'indicator': {'id': indicator, 'value': 'Test Indicator'},
            'country': {'id': country, 'value': 'Test Country'},
            'countryiso3code': country,
            'date': str(end_year),
            'value': 1000000,
            'unit': '',
            'obs_status': '',
            'decimal': 0
        }]
    ]

@pytest.mark.parametrize("mock_successful_response,indicator,country,start_year,end_year", [
    (('NY.GDP.MKTP.CD', 'USA', 2020, 2020), 'NY.GDP.MKTP.CD', 'USA', 2020, 2020),
    (('SP.POP.TOTL', 'CHN', 2019, 2020), 'SP.POP.TOTL', 'CHN', 2019, 2020),
    (('FP.CPI.TOTL.ZG', 'JPN', 2018, 2020), 'FP.CPI.TOTL.ZG', 'JPN', 2018, 2020),
], indirect=['mock_successful_response'])
@responses.activate
def test_fetch_indicator_data_success(world_bank_api, mock_successful_response, indicator, country, start_year, end_year):
    url = f"{world_bank_api.base_url}/country/{country}/indicator/{indicator}"
    responses.add(responses.GET, url, json=mock_successful_response, status=200)
    
    data = world_bank_api.fetch_indicator_data(indicator, country, start_year, end_year)
    
    assert len(data) == 1
    assert data[0]['countryiso3code'] == country
    assert int(data[0]['date']) >= start_year
    assert int(data[0]['date']) <= end_year

@responses.activate
def test_fetch_indicator_data_connection_error(world_bank_api):
    url = f"{world_bank_api.base_url}/country/USA/indicator/NY.GDP.MKTP.CD"
    responses.add(responses.GET, url, body=ConnectionError("Connection failed"))
    
    with pytest.raises(WorldBankAPIError, match="Max retries reached for indicator: NY.GDP.MKTP.CD"):
        world_bank_api.fetch_indicator_data('NY.GDP.MKTP.CD', 'USA', 2020, 2020)

@responses.activate
def test_fetch_indicator_data_http_error(world_bank_api):
    url = f"{world_bank_api.base_url}/country/USA/indicator/NY.GDP.MKTP.CD"
    responses.add(responses.GET, url, json={"error": "Not Found"}, status=404)
    
    with pytest.raises(WorldBankAPIError, match="HTTP error fetching data for NY.GDP.MKTP.CD: 404 Client Error: Not Found for url:"):
        world_bank_api.fetch_indicator_data('NY.GDP.MKTP.CD', 'USA', 2020, 2020)

@responses.activate
def test_fetch_indicator_data_malformed_json(world_bank_api):
    url = f"{world_bank_api.base_url}/country/USA/indicator/NY.GDP.MKTP.CD"
    responses.add(responses.GET, url, body="Invalid JSON", status=200)
    
    with pytest.raises(WorldBankAPIError, match="Error parsing JSON response for indicator: NY.GDP.MKTP.CD"):
        world_bank_api.fetch_indicator_data('NY.GDP.MKTP.CD', 'USA', 2020, 2020)

def test_fetch_indicator_data_invalid_date_range(world_bank_api):
    with pytest.raises(ValueError, match="End year must be greater than or equal to start year"):
        world_bank_api.fetch_indicator_data('NY.GDP.MKTP.CD', 'USA', 2021, 2020)

@responses.activate
def test_fetch_all_data_success(world_bank_api):
    urls = [
        f"{world_bank_api.base_url}/country/USA/indicator/NY.GDP.MKTP.CD",
        f"{world_bank_api.base_url}/country/USA/indicator/SP.POP.TOTL"
    ]
    for url in urls:
        responses.add(responses.GET, url, json=[
            {'page': 1, 'pages': 1, 'per_page': 50, 'total': 1},
            [{'indicator': {'id': 'TEST', 'value': 'Test'}, 'country': {'id': 'USA', 'value': 'United States'}, 'countryiso3code': 'USA', 'date': '2020', 'value': 1000000}]
        ], status=200)
    
    queries = [('NY.GDP.MKTP.CD', ['USA'], 2020, 2020), ('SP.POP.TOTL', ['USA'], 2020, 2020)]
    results = world_bank_api.fetch_all_data(queries)
    
    assert len(results) == 2
    assert all(len(data) == 1 for data in results.values())

@responses.activate
def test_fetch_all_data_partial_failure(world_bank_api):
    url1 = f"{world_bank_api.base_url}/country/USA/indicator/NY.GDP.MKTP.CD"
    url2 = f"{world_bank_api.base_url}/country/USA/indicator/INVALID_INDICATOR"
    responses.add(responses.GET, url1, json=[
        {'page': 1, 'pages': 1, 'per_page': 50, 'total': 1},
        [{'indicator': {'id': 'NY.GDP.MKTP.CD', 'value': 'GDP'}, 'country': {'id': 'USA', 'value': 'United States'}, 'countryiso3code': 'USA', 'date': '2020', 'value': 1000000}]
    ], status=200)
    responses.add(responses.GET, url2, json={"error": "Not Found"}, status=404)
    
    queries = [('NY.GDP.MKTP.CD', ['USA'], 2020, 2020), ('INVALID_INDICATOR', ['USA'], 2020, 2020)]
    results = world_bank_api.fetch_all_data(queries)
    
    assert len(results) == 1
    assert 'NY.GDP.MKTP.CD' in results
    assert len(results['NY.GDP.MKTP.CD']) == 1

if __name__ == '__main__':
    pytest.main(['-n', 'auto', '--dist', 'loadfile'])