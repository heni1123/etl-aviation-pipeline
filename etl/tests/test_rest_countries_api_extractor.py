try:
    from extractors.rest_countries_api_extractor import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_extract_happy_path(mock_http_session):
    """Test extract method with valid input."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value=[{"name": "Country1"}]))
    extractor = RestCountriesExtractor({"url": "http://example.com/{origin_country}", "params": {"origin_country": "Country1", "fields": "name"}})
    result = await extractor.extract()
    assert result == [{"name": "Country1"}]

@pytest.mark.asyncio
async def test_extract_empty_input():
    """Test extract method with empty input."""
    extractor = RestCountriesExtractor({"url": "http://example.com/{origin_country}", "params": {}})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_extract_error_handling(mock_http_session):
    """Test extract method error handling for non-200 response."""
    mock_http_session.get.return_value = AsyncMock(status=404)
    extractor = RestCountriesExtractor({"url": "http://example.com/{origin_country}", "params": {"origin_country": "Country1", "fields": "name"}})
    with pytest.raises(Exception):
        await extractor.extract()

@pytest.mark.asyncio
async def test_fetch_page_happy_path(mock_http_session):
    """Test _fetch_page method with valid parameters."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value={"data": "value"}))
    extractor = RestCountriesExtractor({"url": "http://example.com/{origin_country}", "params": {"origin_country": "Country1", "fields": "name"}})
    result = await extractor._fetch_page({"origin_country": "Country1"})
    assert result == {"data": "value"}

@pytest.mark.asyncio
async def test_fetch_page_empty_input():
    """Test _fetch_page method with empty parameters."""
    extractor = RestCountriesExtractor({"url": "http://example.com/{origin_country}", "params": {}})
    result = await extractor._fetch_page({})
    assert result is None

@pytest.mark.asyncio
async def test_fetch_page_error_handling(mock_http_session):
    """Test _fetch_page method error handling for non-200 response."""
    mock_http_session.get.return_value = AsyncMock(status=500)
    extractor = RestCountriesExtractor({"url": "http://example.com/{origin_country}", "params": {"origin_country": "Country1", "fields": "name"}})
    with pytest.raises(Exception):
        await extractor._fetch_page({"origin_country": "Country1"})

@pytest.mark.asyncio
async def test_handle_rate_limit(mock_http_session):
    """Test _handle_rate_limit method for rate limit response."""
    extractor = RestCountriesExtractor({"url": "http://example.com/{origin_country}", "params": {}})
    mock_response = AsyncMock(headers={"Retry-After": "1"})
    await extractor._handle_rate_limit(mock_response)

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session):
    """Test _retry_with_backoff method with successful retry."""
    mock_http_session.get.side_effect = [AsyncMock(status=500), AsyncMock(status=200, json=AsyncMock(return_value={"data": "value"}))]
    extractor = RestCountriesExtractor({"url": "http://example.com/{origin_country}", "params": {}})
    result = await extractor._retry_with_backoff(mock_http_session.get, "http://example.com/{origin_country}")
    assert result == {"data": "value"}

@pytest.mark.asyncio
async def test_retry_with_backoff_error_handling(mock_http_session):
    """Test _retry_with_backoff method error handling after max attempts."""
    mock_http_session.get.side_effect = AsyncMock(side_effect=Exception("Network error"))
    extractor = RestCountriesExtractor({"url": "http://example.com/{origin_country}", "params": {}})
    with pytest.raises(Exception):
        await extractor._retry_with_backoff(mock_http_session.get, "http://example.com/{origin_country}")

@pytest.mark.asyncio
async def test_close():
    """Test close method to ensure session is closed."""
    extractor = RestCountriesExtractor({"url": "http://example.com/{origin_country}", "params": {}})
    await extractor.close()