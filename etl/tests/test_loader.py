import pytest
import httpx
from unittest.mock import AsyncMock
from src.loader import Loader  # Assuming the Loader class is defined in src.loader

@pytest.fixture
async def mock_httpx_client():
    async with httpx.AsyncClient(transport=httpx.MockTransport()) as client:
        yield client

@pytest.mark.asyncio
async def test_truncate_insert_happy_path(mock_httpx_client):
    loader = Loader(mock_httpx_client)
    await loader.truncate_insert()
    # Add assertions to verify the data was inserted correctly

@pytest.mark.asyncio
async def test_truncate_insert_null_values(mock_httpx_client):
    mock_httpx_client.get = AsyncMock(return_value=httpx.Response(200, json={"states": [None]}))
    loader = Loader(mock_httpx_client)
    await loader.truncate_insert()
    # Add assertions to verify handling of null values

@pytest.mark.asyncio
async def test_truncate_insert_rate_limit(mock_httpx_client):
    mock_httpx_client.get = AsyncMock(side_effect=httpx.HTTPStatusError("Rate limit exceeded", request=None))
    loader = Loader(mock_httpx_client)
    with pytest.raises(httpx.HTTPStatusError):
        await loader.truncate_insert()

@pytest.mark.asyncio
async def test_truncate_insert_empty_response(mock_httpx_client):
    mock_httpx_client.get = AsyncMock(return_value=httpx.Response(200, json={"states": []}))
    loader = Loader(mock_httpx_client)
    await loader.truncate_insert()
    # Add assertions to verify handling of empty response

@pytest.mark.asyncio
async def test_business_rule_altitude_category(mock_httpx_client):
    mock_httpx_client.get = AsyncMock(return_value=httpx.Response(200, json={"states": [{"baro_altitude": None, "on_ground": True}]}))
    loader = Loader(mock_httpx_client)
    result = await loader.truncate_insert()
    # Add assertions to verify altitude category is 'Ground'

@pytest.mark.asyncio
async def test_business_rule_speed_category(mock_httpx_client):
    mock_httpx_client.get = AsyncMock(return_value=httpx.Response(200, json={"states": [{"velocity": None, "on_ground": True}]}))
    loader = Loader(mock_httpx_client)
    result = await loader.truncate_insert()
    # Add assertions to verify speed category is 'Unknown/Ground'