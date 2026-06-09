import asyncio
import logging
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class Orchestrator:
    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def extract(self) -> List[Dict[str, Any]]:
        self.logger.info("Starting extraction phase")
        start_time = asyncio.get_event_loop().time()
        try:
            states = await self.fetch_opensky_states()
            callsign_data = await self.fetch_adsbdb_callsign(states)
            countries_data = await self.fetch_rest_countries(callsign_data)
            self.logger.info("Extraction phase completed successfully")
            return states, callsign_data, countries_data
        except Exception as e:
            self.logger.error(f"Extraction phase failed: {e}")
            raise

    async def fetch_opensky_states(self) -> List[Dict[str, Any]]:
        url = "https://opensky-network.org/api/states/all"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                return data['states']

    async def fetch_adsbdb_callsign(self, states: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_callsign_data(state[1], session) for state in states if state[1]]
            return await asyncio.gather(*tasks)

    async def fetch_callsign_data(self, callsign: str, session: aiohttp.ClientSession) -> Optional[Dict[str, Any]]:
        url = f"https://api.adsbdb.com/v0/callsign/{callsign}"
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
            return data['response']

    async def fetch_rest_countries(self, callsign_List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_country_data(data['origin_country'], session) for data in callsign_data if 'origin_country' in data]
            return await asyncio.gather(*tasks)

    async def fetch_country_data(self, country_code: str, session: aiohttp.ClientSession) -> Optional[Dict[str, Any]]:
        url = f"https://restcountries.com/v3.1/alpha/{country_code}"
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
            return data[0]

    async def transform(self, states: List[Dict[str, Any]], callsign_List[Dict[str, Any]], countries_List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.logger.info("Starting transformation phase")
        transformed_rows = []
        for state in states:
            transformed_row = {
                "icao24": state[0],
                "callsign": state[1].strip().upper() if state[1] else None,
                "origin_country": state[2],
                "time_position": state[3],
                # Add other transformations as needed
            }
            transformed_rows.append(transformed_row)
        self.logger.info("Transformation phase completed successfully")
        return transformed_rows

    async def validate(self, transformed_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.logger.info("Starting validation phase")
        valid_rows = []
        for row in transformed_rows:
            if row['icao24'] is not None and row['time_position'] > 0:
                valid_rows.append(row)
        self.logger.info("Validation phase completed successfully")
        return valid_rows

    async def load(self, valid_rows: List[Dict[str, Any]]) -> None:
        self.logger.info("Starting load phase")
        # Implement the loading logic to PostgreSQL
        # Example: using asyncpg to connect and execute insert statements
        self.logger.info("Load phase completed successfully")

    async def run(self) -> None:
        try:
            states, callsign_data, countries_data = await self.extract()
            transformed_rows = await self.transform(states, callsign_data, countries_data)
            valid_rows = await self.validate(transformed_rows)
            await self.load(valid_rows)
        except Exception as e:
            self.logger.error(f"ETL process failed: {e}")

if __name__ == "__main__":
    orchestrator = Orchestrator()
    asyncio.run(orchestrator.run())