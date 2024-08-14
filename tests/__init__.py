import pytest

@pytest.fixture(autouse=True)
def enable_async_loop():
    """
    This fixture enables the async event loop for all tests.
    It's automatically used due to the 'autouse=True' parameter.
    """
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()
