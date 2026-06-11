import pytest
from unittest import mock

@pytest.fixture
def sample_records():
    """Provides a list of valid records matching the target_data schema."""
    return [
        {"id": 1, "name": "John Doe", "age": 30, "email": "john.doe@example.com"},
        {"id": 2, "name": "Jane Smith", "age": 25, "email": "jane.smith@example.com"},
        {"id": 3, "name": "Alice Johnson", "age": 28, "email": "alice.johnson@example.com"},
    ]

@pytest.fixture
def empty_records():
    """Provides an empty list of records."""
    return []

@pytest.fixture
def invalid_records():
    """Provides a list of records with missing or invalid required fields."""
    return [
        {"id": None, "name": "Invalid User", "age": 22, "email": "invalid@example.com"},
        {"id": "invalid_type", "name": None, "age": 25, "email": "invalid@example.com"},
        {},
    ]

@pytest.fixture
async def mock_db_connection():
    """Mocks asyncpg.Connection or sqlalchemy Engine connection."""
    with mock.patch('asyncpg.connect', create=True) as mock_connect:
        mock_conn = mock.AsyncMock()
        mock_conn.fetch.return_value = [{"id": 1, "name": "John Doe"}]
        mock_conn.execute.return_value = None
        mock_conn.fetchrow.return_value = {"id": 1, "name": "John Doe"}
        mock_conn.fetchval.return_value = 1
        mock_connect.return_value = mock_conn
        yield mock_conn

@pytest.fixture
async def mock_http_session():
    """Mocks aiohttp.ClientSession."""
    with mock.patch('aiohttp.ClientSession', create=True) as mock_session:
        mock_instance = mock.AsyncMock()
        mock_instance.get.return_value.__aenter__.return_value = mock.AsyncMock(json=mock.AsyncMock(return_value={}))
        mock_instance.post.return_value.__aenter__.return_value = mock.AsyncMock(json=mock.AsyncMock(return_value={}))
        mock_session.return_value = mock_instance
        yield mock_instance

pytest_plugins = ["pytest_asyncio"]
asyncio_mode = "auto"