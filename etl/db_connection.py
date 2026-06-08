import asyncpg
import logging
from typing import Any, Dict, List

class DatabaseConnection:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool = None

    async def connect(self) -> None:
        try:
            self.pool = await asyncpg.create_pool(self.database_url)
            logging.info("Database connection pool created successfully.")
        except Exception as e:
            logging.error(f"Error creating database connection pool: {e}")
            raise

    async def close(self) -> None:
        if self.pool:
            await self.pool.close()
            logging.info("Database connection pool closed.")

    async def execute(self, query: str, *args: Any) -> None:
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                try:
                    await connection.execute(query, *args)
                except Exception as e:
                    logging.error(f"Error executing query: {query} | Error: {e}")
                    raise

    async def fetch(self, query: str, *args: Any) -> List[Dict[str, Any]]:
        async with self.pool.acquire() as connection:
            try:
                return await connection.fetch(query, *args)
            except Exception as e:
                logging.error(f"Error fetching data with query: {query} | Error: {e}")
                raise

database_url = "postgresql://user:password@localhost:5432/aviation_db"
db_connection = DatabaseConnection(database_url)