import asyncio
import logging
import os
from typing import List, Dict, Any, Optional
import aiohttp
from datetime import datetime

class Orchestrator:
    def __init__(self, db_connection_string: str):
        self.db_connection_string = db_connection_string
        self.api_urls = {
            "src_opensky_states": "https://opensky-network.org/api/states/all",
            "src_adsbdb_callsign": "https://api.adsbdb.com/v0/callsign/{callsign}",
            "src_rest_countries": "https://restcountries.com/v3.1/alpha/{origin_country}"
        }
        logging.basicConfig(level=logging.INFO)

    async def extract(self) -> List[Dict[str, Any]]:
        logging.info("Starting extraction phase")
        start_time = datetime.now()
        async with aiohttp.ClientSession() as session:
            try:
                open_sky_data = await self.fetch_data(session, self.api_urls["src_opensky_states"])
                return open_sky_data
            except Exception as e:
                logging.error(f"Error during extraction: {e}")
                raise

    async def fetch_data(self, session: aiohttp.ClientSession, url: str) -> List[Dict[str, Any]]:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    async def join(self, List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        logging.info("Starting join phase")
        start_time = datetime.now()
        enriched_data = []
        async with aiohttp.ClientSession() as session:
            for row in data:
                try:
                    callsign_info = await self.fetch_data(session, self.api_urls["src_adsbdb_callsign"].format(callsign=row.get('callsign')))
                    row['callsign_info'] = callsign_info.get('response', {})
                    country_info = await self.fetch_data(session, self.api_urls["src_rest_countries"].format(origin_country=row.get('origin_country')))
                    row['country_info'] = country_info.get('data', {})
                    enriched_data.append(row)
                except Exception as e:
                    logging.warning(f"Enrichment failed for row {row}: {e}")
                    enriched_data.append(row)  # Append row with NULL fields
        return enriched_data

    async def transform(self, List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        logging.info("Starting transform phase")
        transformed_data = []
        for row in data:
            transformed_row = self.apply_business_rules(row)
            transformed_data.append(transformed_row)
        return transformed_data

    def apply_business_rules(self, row: Dict[str, Any]) -> Dict[str, Any]:
        if row.get('baro_altitude') is None or row.get('on_ground') is True:
            row['altitude_category'] = 'Ground'
        elif 0 < row.get('baro_altitude') <= 3000:
            row['altitude_category'] = 'Low Altitude'
        elif 3000 < row.get('baro_altitude') <= 7500:
            row['altitude_category'] = 'Mid Altitude'
        elif 7500 < row.get('baro_altitude') <= 12500:
            row['altitude_category'] = 'Cruise Altitude'
        else:
            row['altitude_category'] = 'High Altitude'

        if row.get('velocity') is None or row.get('on_ground') == 'Unknown/Ground':
            row['speed_category'] = 'Unknown/Ground'
        elif row.get('velocity') < 100:
            row['speed_category'] = 'Slow'
        elif row.get('velocity') < 300:
            row['speed_category'] = 'Medium'
        else:
            row['speed_category'] = 'Fast'

        return row

    async def load(self, List[Dict[str, Any]]) -> None:
        logging.info("Starting load phase")
        start_time = datetime.now()
        # Here you would implement the logic to load data into the PostgreSQL database
        # For example, using an async database library like asyncpg
        # await self.db.load_data(data)
        logging.info("Load phase completed")

    async def run(self) -> None:
        try:
            extracted_data = await self.extract()
            joined_data = await self.join(extracted_data)
            transformed_data = await self.transform(joined_data)
            await self.load(transformed_data)
        except Exception as e:
            logging.error(f"ETL process failed: {e}")

if __name__ == "__main__":
    db_connection_string = os.getenv("DB_CONNECTION_STRING")
    orchestrator = Orchestrator(db_connection_string)
    asyncio.run(orchestrator.run())