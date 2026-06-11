import os
import logging
import aiohttp
import asyncio
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)

class DataIngestion:
    def __init__(self, task_id: str, task_category: str, task_priority: str) -> None:
        self.task_id = task_id
        self.task_category = task_category
        self.task_priority = task_priority
        self.api_url = "https://restcountries.com/v3.1/all"
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.db_password = os.getenv("DB_PASSWORD")

    async def fetch_data(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        try:
            async with session.get(self.api_url) as response:
                response.raise_for_status()
                data = await response.json()
                logging.info("Data fetched successfully from REST Countries API.")
                return data
        except Exception as e:
            logging.error(f"Error fetching {e}")
            return {}

    async def ingest_data(self) -> None:
        async with aiohttp.ClientSession() as session:
            data = await self.fetch_data(session)
            if data:
                self.process_data(data)

    def process_data(self, Dict[str, Any]) -> None:
        for country in data:
            country_name = country.get("name", {}).get("common", "Unknown")
            logging.info(f"Processing country: {country_name}")
            # Here you would implement the logic to insert or update the data in the target database

    async def run(self) -> None:
        await self.ingest_data()

async def main() -> None:
    ingestion = DataIngestion(task_id="pipe_001", task_category="data_pipeline", task_priority="high")
    await ingestion.run()

if __name__ == "__main__":
    asyncio.run(main())