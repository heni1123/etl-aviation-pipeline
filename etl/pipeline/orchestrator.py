import asyncio
import logging
import os
import time
from typing import List, Dict, Any, Optional
import aiohttp

class Orchestrator:
    def __init__(self, db_connection_string: str):
        self.db_connection_string = db_connection_string
        self.logger = self.setup_logging()

    def setup_logging(self) -> logging.Logger:
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)

    async def fetch_opensky_states(self) -> List[Dict[str, Any]]:
        url = "https://opensky-network.org/api/states/all"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    self.logger.error("Failed to fetch OpenSky states")
                    raise Exception("Primary source failure")
                return await response.json()

    async def fetch_adsbdb_callsign(self, callsign: str) -> Optional[Dict[str, Any]]:
        url = f"https://api.adsbdb.com/v0/callsign/{callsign}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    self.logger.warning(f"Failed to fetch callsign data for {callsign}")
                    return None
                return await response.json()

    async def fetch_rest_countries(self, origin_country: str) -> Optional[Dict[str, Any]]:
        url = f"https://restcountries.com/v3.1/alpha/{origin_country}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    self.logger.warning(f"Failed to fetch country data for {origin_country}")
                    return None
                return await response.json()

    async def extract(self) -> List[Dict[str, Any]]:
        start_time = time.time()
        self.logger.info("Starting extraction phase")
        try:
            opensky_data = await self.fetch_opensky_states()
            self.logger.info("OpenSky data extracted successfully")
            return opensky_data['states']
        except Exception as e:
            self.logger.error(f"Extraction failed: {e}")
            raise

    async def enrich_data(self, states: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        enriched_data = []
        for state in states:
            callsign_data = await self.fetch_adsbdb_callsign(state.get('callsign', ''))
            if callsign_data:
                state['callsign_info'] = callsign_data['response']
            else:
                state['callsign_info'] = None

            country_data = await self.fetch_rest_countries(state.get('origin_country', ''))
            if country_data:
                state['country_info'] = country_data[0] if isinstance(country_data, list) else None
            else:
                state['country_info'] = None

            enriched_data.append(state)
        return enriched_data

    async def transform(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        transformed_rows = []
        for row in rows:
            transformed_row = row.copy()
            transformed_row['altitude_category'] = self.categorize_altitude(row.get('baro_altitude'), row.get('on_ground'))
            transformed_row['speed_category'] = self.categorize_speed(row.get('velocity'), row.get('on_ground'))
            transformed_rows.append(transformed_row)
        return transformed_rows

    def categorize_altitude(self, baro_altitude: Optional[float], on_ground: Optional[bool]) -> Optional[str]:
        if baro_altitude is None or on_ground:
            return 'Ground'
        elif 0 < baro_altitude <= 3000:
            return 'Low Altitude'
        elif 3000 < baro_altitude <= 7500:
            return 'Mid Altitude'
        elif 7500 < baro_altitude <= 12500:
            return 'Cruise Altitude'
        elif baro_altitude > 12500:
            return 'High Altitude'
        return None

    def categorize_speed(self, velocity: Optional[float], on_ground: Optional[bool]) -> Optional[str]:
        if velocity is None or on_ground:
            return 'Unknown/Ground'
        elif velocity < 20:
            return 'Taxi'
        elif velocity < 100:
            return 'Low Speed'
        elif velocity < 300:
            return 'Cruising Speed'
        return 'High Speed'

    async def load(self, transformed_rows: List[Dict[str, Any]]):
        # Placeholder for loading logic
        self.logger.info("Loading transformed data into the database")

    async def run(self):
        start_time = time.time()
        try:
            states = await self.extract()
            enriched_data = await self.enrich_data(states)
            transformed_rows = await self.transform(enriched_data)
            await self.load(transformed_rows)
        except Exception as e:
            self.logger.error(f"ETL process failed: {e}")
        finally:
            duration = time.time() - start_time
            self.logger.info(f"ETL process completed in {duration:.2f} seconds")

if __name__ == "__main__":
    orchestrator = Orchestrator(db_connection_string=os.getenv("DATABASE_URL"))
    asyncio.run(orchestrator.run())