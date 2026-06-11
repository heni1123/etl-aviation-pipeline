try:
    from extractors.adsbdb_api_extractor import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_extract_happy_path(mock_http_session):
    """Test extract method with valid input, expect success."""
    mock_http_session.get = AsyncMock(return_value=AsyncMock(status=200, json=AsyncMock(return_value=[{"data": "value"}])))
    extractor = AdsbdbExtractor({"url": "http://example.com/{callsign}"})
    result = await extractor.extract()
    assert result == [{"data": "value"}, {"data": "value"}]

@pytest.mark.asyncio
async def test_extract_empty_input(mock_http_session):
    """Test extract method with empty input, expect success."""
    mock_http_session.get = AsyncMock(side_effect=Exception("No callsigns"))
    extractor = AdsbdbExtractor({"url": "http://example.com/{callsign}"})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_extract_error_handling(mock_http_session):
    """Test extract method with error handling, expect logged error."""
    mock_http_session.get = AsyncMock(side_effect=Exception("Network error"))
    extractor = AdsbdbExtractor({"url": "http://example.com/{callsign}"})
    with mock.patch.object(extractor.logger, 'error') as mock_logger:
        result = await extractor.extract()
        assert result == []
        mock_logger.assert_called_with("Error extracting data for CALLSIGN1: Network error")

@pytest.mark.asyncio
async def test_fetch_page_happy_path(mock_http_session):
    """Test _fetch_page method with valid callsign, expect success."""
    mock_http_session.get = AsyncMock(return_value=AsyncMock(status=200, json=AsyncMock(return_value={"data": "value"})))
    extractor = AdsbdbExtractor({"url": "http://example.com/{callsign}"})
    result = await extractor._fetch_page("CALLSIGN1")
    assert result == {"data": "value"}

@pytest.mark.asyncio
async def test_fetch_page_rate_limit_handling(mock_http_session):
    """Test _fetch_page method with rate limit, expect retry."""
    mock_http_session.get = AsyncMock(side_effect=[AsyncMock(status=429), AsyncMock(status=200, json=AsyncMock(return_value={"data": "value"}))])
    extractor = AdsbdbExtractor({"url": "http://example.com/{callsign}"})
    result = await extractor._fetch_page("CALLSIGN1")
    assert result == {"data": "value"}

@pytest.mark.asyncio
async def test_fetch_page_error_handling(mock_http_session):
    """Test _fetch_page method with unrecoverable error, expect exception."""
    mock_http_session.get = AsyncMock(return_value=AsyncMock(status=404))
    extractor = AdsbdbExtractor({"url": "http://example.com/{callsign}"})
    with pytest.raises(Exception, match="Unrecoverable error: 404"):
        await extractor._fetch_page("CALLSIGN1")

@pytest.mark.asyncio
async def test_handle_rate_limit(mock_http_session):
    """Test _handle_rate_limit method, expect sleep and retry."""
    extractor = AdsbdbExtractor({"url": "http://example.com/{callsign}"})
    with mock.patch('asyncio.sleep', return_value=None) as mock_sleep:
        await extractor._handle_rate_limit(AsyncMock())
        mock_sleep.assert_called_once_with(5)

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session):
    """Test _retry_with_backoff method with successful call, expect success."""
    mock_http_session.get = AsyncMock(return_value=AsyncMock(status=200, json=AsyncMock(return_value={"data": "value"})))
    extractor = AdsbdbExtractor({"url": "http://example.com/{callsign}"})
    result = await extractor._retry_with_backoff(mock_http_session.get, "http://example.com/CALLSIGN1")
    assert result == {"data": "value"}

@pytest.mark.asyncio
async def test_retry_with_backoff_error_handling(mock_http_session):
    """Test _retry_with_backoff method with failure, expect exception."""
    mock_http_session.get = AsyncMock(side_effect=aiohttp.ClientError("Client error"))
    extractor = AdsbdbExtractor({"url": "http://example.com/{callsign}"})
    with pytest.raises(aiohttp.ClientError):
        await extractor._retry_with_backoff(mock_http_session.get, "http://example.com/CALLSIGN1")

@pytest.mark.asyncio
async def test_close(mock_http_session):
    """Test close method, expect session to close without errors."""
    extractor = AdsbdbExtractor({"url": "http://example.com/{callsign}"})
    await extractor.close()  # No assertion needed, just ensure it runs without error.