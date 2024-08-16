import pytest
from dash.testing.application_runners import import_app
from dash.testing.composite import DashComposite
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from src.dashboard import create_dashboard
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def test_data():
    date_range = pd.date_range(start='2018', periods=3, freq='YE')
    countries = ['USA', 'CHN', 'JPN']
    
    gdp_data = pd.DataFrame({
        'USA': [19294482071552.0, 20527159000000.0, 21372344689888.0],
        'CHN': [11226186233480.0, 12261432088889.0, 13895361427169.0],
        'JPN': [5176932949853.21, 5231739379456.18, 5058169401967.53]
    }, index=date_range)
    
    pop_data = pd.DataFrame({
        'USA': [326687501, 328239523, 329484123],
        'CHN': [1395380000, 1397715000, 1400050000],
        'JPN': [126529100, 126226568, 125836021]
    }, index=date_range)
    
    gdp_df = gdp_data.stack().reset_index()
    gdp_df.columns = ['year', 'country_code', 'NY.GDP.MKTP.CD']
    gdp_df['country_name'] = gdp_df['country_code']
    
    pop_df = pop_data.stack().reset_index()
    pop_df.columns = ['year', 'country_code', 'SP.POP.TOTL']
    pop_df['country_name'] = pop_df['country_code']
    
    return {
        'NY.GDP.MKTP.CD': gdp_df.set_index(['country_name', 'country_code', 'year']),
        'SP.POP.TOTL': pop_df.set_index(['country_name', 'country_code', 'year'])
    }

@pytest.fixture
def indicators_standard():
    return {
        "Economic": ["NY.GDP.MKTP.CD"],
        "Demographic": ["SP.POP.TOTL"]
    }

@pytest.fixture
def indicator_mapping():
    return {
        "NY.GDP.MKTP.CD": "GDP (current US$)",
        "SP.POP.TOTL": "Population, total"
    }

@pytest.fixture
def dash_app(test_data, indicators_standard, indicator_mapping):
    app = create_dashboard(test_data, indicators_standard, indicator_mapping)
    return app

@pytest.fixture(scope="session")
def driver():
    drivers = [
        ('Chrome', lambda: webdriver.Chrome(ChromeDriverManager().install(), options=ChromeOptions())),
        ('Firefox', lambda: webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=FirefoxOptions())),
        ('Safari', lambda: webdriver.Safari(options=SafariOptions()))
    ]

    for name, driver_func in drivers:
        try:
            logger.info(f"Attempting to initialize {name} driver")
            driver = driver_func()
            logger.info(f"Successfully initialized {name} driver")
            yield driver
            driver.quit()
            return
        except Exception as e:
            logger.error(f"Failed to initialize {name} driver: {str(e)}")

    pytest.skip("Could not initialize any WebDriver")

@pytest.fixture
def dash_duo(dash_app, driver, request):
    return DashComposite(dash_app, driver, request.config.option.server_url)

def test_create_dashboard(dash_app):
    assert dash_app.layout is not None

def test_update_indicator_dropdown(dash_duo):
    dash_duo.wait_for_element("#category-dropdown", timeout=4)
    
    # Test Economic category
    dash_duo.select_dcc_dropdown("#category-dropdown", "Economic")
    dash_duo.wait_for_element("#indicator-dropdown", timeout=4)
    indicator_options = dash_duo.find_elements("#indicator-dropdown option")
    assert len(indicator_options) == 1
    assert indicator_options[0].get_attribute("value") == "NY.GDP.MKTP.CD"

    # Test Demographic category
    dash_duo.select_dcc_dropdown("#category-dropdown", "Demographic")
    dash_duo.wait_for_element("#indicator-dropdown", timeout=4)
    indicator_options = dash_duo.find_elements("#indicator-dropdown option")
    assert len(indicator_options) == 1
    assert indicator_options[0].get_attribute("value") == "SP.POP.TOTL"

def test_update_main_graph(dash_duo, test_data):
    dash_duo.wait_for_element("#indicator-dropdown", timeout=4)
    
    # Test graph update for GDP
    dash_duo.select_dcc_dropdown("#indicator-dropdown", "NY.GDP.MKTP.CD")
    dash_duo.multiple_select_dcc_dropdown("#country-dropdown", ["USA", "CHN"])
    
    dash_duo.wait_for_element("#main-graph", timeout=4)
    assert dash_duo.find_element("#main-graph").get_attribute("data-dash-is-loading") == "false"
    
    dash_duo.wait_for_element("#main-graph .js-plotly-plot", timeout=4)

def test_update_bar_chart(dash_duo, test_data):
    dash_duo.wait_for_element("#indicator-dropdown", timeout=4)
    
    # Test bar chart update for GDP
    dash_duo.select_dcc_dropdown("#indicator-dropdown", "NY.GDP.MKTP.CD")
    dash_duo.multiple_select_dcc_dropdown("#country-dropdown", ["USA", "CHN"])
    
    dash_duo.wait_for_element("#bar-chart", timeout=4)
    assert dash_duo.find_element("#bar-chart").get_attribute("data-dash-is-loading") == "false"
    
    dash_duo.wait_for_element("#bar-chart .js-plotly-plot", timeout=4)

def test_update_scatter_plot(dash_duo, test_data):
    dash_duo.wait_for_element("#category-dropdown", timeout=4)
    
    # Test scatter plot update for Economic category
    dash_duo.select_dcc_dropdown("#category-dropdown", "Economic")
    dash_duo.multiple_select_dcc_dropdown("#country-dropdown", ["USA", "CHN"])
    
    dash_duo.wait_for_element("#scatter-plot", timeout=4)
    assert dash_duo.find_element("#scatter-plot").get_attribute("data-dash-is-loading") == "false"
    
    dash_duo.wait_for_element("#scatter-plot .js-plotly-plot", timeout=4)

if __name__ == '__main__':
    pytest.main([__file__])
