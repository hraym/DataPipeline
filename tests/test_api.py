import pytest
import aiohttp
from src.api import WorldBankAPI
from src.exceptions import WorldBankAPIError

@pytest.mark.asyncio
async def test_fetch_data():
    api = WorldBankAPI('http://api.worldbank.org/v2')
    async with aiohttp.ClientSession() as session:
        data = await api.fetch_data(session, 'NY.GDP.MKTP.CD', ['USA'], 2000, 2020)
        assert len(data) > 0

@pytest.mark.asyncio
async def test_fetch_data_invalid_indicator():
    api = WorldBankAPI('http://api.worldbank.org/v2')
    async with aiohttp.ClientSession() as session:
        with pytest.raises(WorldBankAPIError):
            await api.fetch_data(session, 'INVALID_INDICATOR', ['USA'], 2000, 2020)