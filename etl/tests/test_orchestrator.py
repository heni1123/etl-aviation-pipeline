try:
    from pipeline.orchestrator import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_run_happy_path(mock_http_session, sample_records):
    """Test run method with valid input, expect success."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value=sample_records))
    orchestrator = PipelineOrchestrator(dry_run=False)
    await orchestrator.run()
    assert orchestrator.metrics['extracted'] == len(sample_records)
    assert orchestrator.metrics['loaded'] == len(sample_records)

@pytest.mark.asyncio
async def test_run_empty_input(mock_http_session):
    """Test run method with empty input, expect success with no loading."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value=[]))
    orchestrator = PipelineOrchestrator(dry_run=False)
    await orchestrator.run()
    assert orchestrator.metrics['extracted'] == 0
    assert orchestrator.metrics['loaded'] == 0

@pytest.mark.asyncio
async def test_run_error_handling(mock_http_session):
    """Test run method with an error during extraction, expect failure."""
    mock_http_session.get.side_effect = Exception("Network error")
    orchestrator = PipelineOrchestrator(dry_run=False)
    await orchestrator.run()
    assert orchestrator.metrics['errors'] == ["Network error"]

@pytest.mark.asyncio
async def test_extract_phase_happy_path(mock_http_session, sample_records):
    """Test extract_phase method with valid input, expect records."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value=sample_records))
    orchestrator = PipelineOrchestrator()
    records = await orchestrator._extract_phase()
    assert records == sample_records
    assert orchestrator.metrics['extracted'] == len(sample_records)

@pytest.mark.asyncio
async def test_extract_phase_empty_input(mock_http_session):
    """Test extract_phase method with empty response, expect empty list."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value=[]))
    orchestrator = PipelineOrchestrator()
    records = await orchestrator._extract_phase()
    assert records == []
    assert orchestrator.metrics['extracted'] == 0

@pytest.mark.asyncio
async def test_extract_phase_error_handling(mock_http_session):
    """Test extract_phase method with a network error, expect exception."""
    mock_http_session.get.return_value = AsyncMock(status=500)
    orchestrator = PipelineOrchestrator()
    with pytest.raises(Exception, match="Failed to fetch 500"):
        await orchestrator._extract_phase()

@pytest.mark.asyncio
async def test_transform_phase_happy_path(sample_records):
    """Test transform_phase method with valid records, expect transformed records."""
    orchestrator = PipelineOrchestrator()
    transformed = await orchestrator._transform_phase(sample_records)
    assert len(transformed) == len(sample_records)

@pytest.mark.asyncio
async def test_transform_phase_empty_input():
    """Test transform_phase method with empty input, expect empty list."""
    orchestrator = PipelineOrchestrator()
    transformed = await orchestrator._transform_phase([])
    assert transformed == []

@pytest.mark.asyncio
async def test_transform_phase_error_handling(invalid_records):
    """Test transform_phase method with invalid records, expect no exception but handle gracefully."""
    orchestrator = PipelineOrchestrator()
    transformed = await orchestrator._transform_phase(invalid_records)
    assert len(transformed) == 0

@pytest.mark.asyncio
async def test_validate_phase_happy_path(sample_records):
    """Test validate_phase method with valid records, expect no exception."""
    orchestrator = PipelineOrchestrator()
    await orchestrator._validate_phase(sample_records)

@pytest.mark.asyncio
async def test_validate_phase_empty_input():
    """Test validate_phase method with empty input, expect no exception."""
    orchestrator = PipelineOrchestrator()
    await orchestrator._validate_phase([])

@pytest.mark.asyncio
async def test_validate_phase_error_handling(invalid_records):
    """Test validate_phase method with invalid records, expect ValueError."""
    orchestrator = PipelineOrchestrator()
    with pytest.raises(ValueError, match="Validation failed: Missing required fields"):
        await orchestrator._validate_phase(invalid_records)

@pytest.mark.asyncio
async def test_load_phase_happy_path(mock_db_connection, sample_records):
    """Test load_phase method with valid records, expect successful load."""
    orchestrator = PipelineOrchestrator(dry_run=False)
    await orchestrator._load_phase(sample_records)
    assert orchestrator.metrics['loaded'] == len(sample_records)

@pytest.mark.asyncio
async def test_load_phase_empty_input(mock_db_connection):
    """Test load_phase method with empty input, expect no load."""
    orchestrator = PipelineOrchestrator(dry_run=False)
    await orchestrator._load_phase([])
    assert orchestrator.metrics['loaded'] == 0

@pytest.mark.asyncio
async def test_load_phase_error_handling(mock_db_connection, invalid_records):
    """Test load_phase method with invalid records, expect exception."""
    mock_db_connection.execute.side_effect = Exception("DB error")
    orchestrator = PipelineOrchestrator(dry_run=False)
    with pytest.raises(Exception, match="DB error"):
        await orchestrator._load_phase(invalid_records)

def test_audit_pipeline_run():
    """Test audit_pipeline_run method, expect logging of metrics."""
    orchestrator = PipelineOrchestrator()
    start_ts = time.time()
    end_ts = time.time() + 1
    orchestrator._audit_pipeline_run(start_ts, end_ts, 'success')
    assert orchestrator.metrics['extracted'] == 0
    assert orchestrator.metrics['loaded'] == 0