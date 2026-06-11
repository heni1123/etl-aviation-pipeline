import asyncio
import logging
import os
from typing import List, Dict, Any
import aiohttp
from dotenv import dotenv_values

class Orchestrator:
    def __init__(self):
        self.logger = self.setup_logging()
        self.api_urls = {
            "opensky": "https://opensky-network.org/api/states/all",
            "adsbdb": "https://api.adsbdb.com/v0/callsign/{callsign}",
            "restcountries": "https://restcountries.com/v3.1/alpha/{code}"
        }

    def setup_logging(self) -> logging.Logger:
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)

    async def fetch_opensky_states(self) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_urls["opensky"]) as response:
                if response.status != 200:
                    self.logger.error("Failed to fetch OpenSky states")
                    raise Exception("Primary source failure")
                return await response.json()

    async def fetch_adsbdb_callsign(self, callsign: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_urls["adsbdb"].format(callsign=callsign)) as response:
                if response.status != 200:
                    self.logger.warning(f"Failed to fetch ADSBDB callsign for {callsign}")
                    return {}
                return await response.json()

    async def fetch_restcountries(self, code: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_urls["restcountries"].format(code=code)) as response:
                if response.status != 200:
                    self.logger.warning(f"Failed to fetch country data for {code}")
                    return {}
                return await response.json()

    async def extract(self) -> List[Dict[str, Any]]:
        self.logger.info("Starting extraction phase")
        try:
            opensky_data = await self.fetch_opensky_states()
            self.logger.info("Extraction phase completed successfully")
            return opensky_data.get('states', [])
        except Exception as e:
            self.logger.error(f"Extraction phase failed: {e}")
            raise

    async def transform(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.logger.info("Starting transformation phase")
        transformed_rows = []
        for row in rows:
            transformed_row = {
                "icao24": row.get("icao24"),
                "callsign": row.get("callsign", "").strip().upper(),
                "origin_country": row.get("origin_country"),
                "time_position": row.get("time_position"),
                # Add other transformations as needed
            }
            transformed_rows.append(transformed_row)
        self.logger.info("Transformation phase completed successfully")
        return transformed_rows

    async def load(self, transformed_rows: List[Dict[str, Any]]) -> None:
        self.logger.info("Starting load phase")
        # Implement the loading logic to the PostgreSQL database
        # For example, using an ORM or raw SQL
        self.logger.info("Load phase completed successfully")

    async def run(self) -> None:
        try:
            extraction_start = asyncio.get_event_loop().time()
            rows = await self.extract()
            extraction_duration = asyncio.get_event_loop().time() - extraction_start
            self.logger.info(f"Extraction duration: {extraction_duration:.2f} seconds")

            transformation_start = asyncio.get_event_loop().time()
            transformed_rows = await self.transform(rows)
            transformation_duration = asyncio.get_event_loop().time() - transformation_start
            self.logger.info(f"Transformation duration: {transformation_duration:.2f} seconds")

            await self.load(transformed_rows)

        except Exception as e:
            self.logger.error(f"ETL process failed: {e}")

if __name__ == "__main__":
    orchestrator = Orchestrator()
    asyncio.run(orchestrator.run())

# Write .env example
with open('.env.example', 'w') as f:
    f.write("DATABASE_URL=postgresql://user:password@localhost:5432/analytics.cible\n")
    f.write("ADSBD_API_KEY=your_adsbdb_api_key\n")
    f.write("OPENSKY_USERNAME=your_opensky_username\n")
    f.write("OPENSKY_PASSWORD=your_opensky_password\n")