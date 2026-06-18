import asyncio
import logging
import os
from typing import List, Dict, Any, Optional
import aiohttp
from datetime import datetime

class Orchestrator:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

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
        self.logger.info("Starting extraction phase")
        start_time = datetime.now()
        try:
            opensky_data = await self.fetch_opensky_states()
            self.logger.info("Extraction phase completed successfully")
            return opensky_data.get('states', [])
        except Exception as e:
            self.logger.error(f"Extraction phase failed: {e}")
            raise

    async def join(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.logger.info("Starting join phase")
        enriched_rows = []
        for row in rows:
            callsign_data = await self.fetch_adsbdb_callsign(row.get('callsign', ''))
            if callsign_data:
                row.update(callsign_data.get('response', {}))
            else:
                self.logger.warning(f"Enrichment failed for callsign: {row.get('callsign', '')}")

            country_data = await self.fetch_rest_countries(row.get('origin_country', ''))
            if country_data:
                row.update(country_data.get('data', {}))
            else:
                self.logger.warning(f"Enrichment failed for origin country: {row.get('origin_country', '')}")

            enriched_rows.append(row)
        self.logger.info("Join phase completed successfully")
        return enriched_rows

    async def transform(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.logger.info("Starting transform phase")
        transformed_rows = []
        for row in rows:
            row['altitude_category'] = self.categorize_altitude(row)
            row['speed_category'] = self.categorize_speed(row)
            transformed_rows.append(row)
        self.logger.info("Transform phase completed successfully")
        return transformed_rows

    def categorize_altitude(self, row: Dict[str, Any]) -> str:
        if row.get('baro_altitude') is None or row.get('on_ground'):
            return 'Ground'
        elif 0 < row['baro_altitude'] <= 3000:
            return 'Low Altitude'
        elif 3000 < row['baro_altitude'] <= 7500:
            return 'Mid Altitude'
        elif 7500 < row['baro_altitude'] <= 12500:
            return 'Cruise Altitude'
        else:
            return 'High Altitude'

    def categorize_speed(self, row: Dict[str, Any]) -> str:
        if row.get('velocity') is None or row.get('on_ground'):
            return 'Unknown/Ground'
        elif row['velocity'] < 100:
            return 'Slow'
        elif 100 <= row['velocity'] < 300:
            return 'Normal'
        else:
            return 'Fast'

    async def load(self, rows: List[Dict[str, Any]]) -> None:
        self.logger.info("Starting load phase")
        # Here you would implement the logic to load data into the database
        # For example, using an ORM or raw SQL
        self.logger.info("Load phase completed successfully")

    async def run(self) -> None:
        try:
            extracted_data = await self.extract()
            joined_data = await self.join(extracted_data)
            transformed_data = await self.transform(joined_data)
            await self.load(transformed_data)
        except Exception as e:
            self.logger.error(f"ETL process failed: {e}")

if __name__ == "__main__":
    orchestrator = Orchestrator()
    asyncio.run(orchestrator.run())