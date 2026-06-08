import asyncio
import logging
from typing import Any, Dict
from db_connection import get_connection_pool

class PipelineLogger:
    def __init__(self):
        self.pool = get_connection_pool()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def log_pipeline_run(self, start_time: str, end_time: str, status: str, rows_extracted: int, rows_loaded: int) -> None:
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                try:
                    await connection.execute("""
                        INSERT INTO analytics.pipeline_runs (start_time, end_time, status, rows_extracted, rows_loaded)
                        VALUES ($1, $2, $3, $4, $5)
                    """, start_time, end_time, status, rows_extracted, rows_loaded)
                    self.logger.info("Pipeline run logged successfully.")
                except Exception as e:
                    self.logger.error(f"Error logging pipeline run: {e}")
                    raise

    async def close(self) -> None:
        await self.pool.close()