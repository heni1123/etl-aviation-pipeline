import asyncio
import logging
import os
from typing import List, Dict, Any, Optional
import aiohttp
from dotenv import dotenv_values

class Orchestrator:
    def __init__(self):
        self.api_urls = {
            "opensky": "https://opensky-network.org/api/states/all",
            "adsbdb": "https://api.adsbdb.com/v0/callsign/{callsign}",
            "restcountries": "https://restcountries.com/v3.1/alpha/{code}"
        }
        self.logger = self.setup_logging()

    def setup_logging(self) -> logging.Logger:
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)

    async def fetch_opensky_states(self) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_urls["opensky"]) as response:
                response.raise_for_status()
                data = await response.json()
                return data['states']

    async def fetch_adsbdb_callsign(self, callsign: str) -> Optional[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_urls["adsbdb"].format(callsign=callsign)) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['response']
                return None

    async def fetch_restcountries(self, code: str) -> Optional[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_urls["restcountries"].format(code=code)) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['data']
                return None

    async def extract(self) -> List[Dict[str, Any]]:
        self.logger.info("Starting extraction phase")
        try:
            opensky_data, adsbdb_data, restcountries_data = await asyncio.gather(
                self.fetch_opensky_states(),
                self.fetch_adsbdb_callsign("some_callsign"),  # Placeholder for actual callsign
                self.fetch_restcountries("US")  # Placeholder for actual country code
            )
            self.logger.info("Extraction phase completed successfully")
            return opensky_data
        except Exception as e:
            self.logger.error(f"Extraction phase failed: {e}")
            raise

    async def transform(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.logger.info("Starting transformation phase")
        transformed_rows = []
        for row in rows:
            transformed_row = {
                "icao24": row['icao24'],
                "callsign": row['callsign'].strip().upper() if row['callsign'] else None,
                "origin_country": row['origin_country'],
                "time_position": row['time_position'],
                "last_contact": row['last_contact'],
                "longitude": row['longitude'],
                "latitude": row['latitude'],
                "on_ground": row['on_ground'],
            }
            transformed_rows.append(transformed_row)
        self.logger.info("Transformation phase completed successfully")
        return transformed_rows

    async def load(self, transformed_rows: List[Dict[str, Any]]) -> None:
        self.logger.info("Starting load phase")
        # Here you would implement the logic to load the data into the database
        # For example, using an ORM or raw SQL
        self.logger.info("Load phase completed successfully")

    async def run(self) -> None:
        try:
            extracted_rows = await self.extract()
            transformed_rows = await self.transform(extracted_rows)
            await self.load(transformed_rows)
        except Exception as e:
            self.logger.error(f"ETL process failed: {e}")

if __name__ == "__main__":
    orchestrator = Orchestrator()
    asyncio.run(orchestrator.run())
    with open('.env.example', 'w') as f:
        f.write("API_OPENSKY_URL=https://opensky-network.org/api/states/all\n")
        f.write("API_ADSBDDB_URL=https://api.adsbdb.com/v0/callsign/{callsign}\n")
        f.write("API_RESTCOUNTRIES_URL=https://restcountries.com/v3.1/alpha/{code}\n")