import asyncio
import logging
import os
from typing import List, Dict, Any, Optional
import aiohttp
from dotenv import dotenv_values

class Orchestrator:
    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO)
        self.api_urls = {
            "src_opensky_states": "https://opensky-network.org/api/states/all",
            "src_adsbdb_callsign": "https://api.adsbdb.com/v0/callsign/{callsign}",
            "src_rest_countries": "https://restcountries.com/v3.1/alpha/{origin_country}"
        }

    async def extract(self) -> List[Dict[str, Any]]:
        logging.info("Starting extraction phase")
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.fetch_data(session, self.api_urls["src_opensky_states"]),
            ]
            primary_data = await asyncio.gather(*tasks)
            if not primary_data[0]:
                logging.error("Primary source extraction failed, aborting ETL process.")
                raise Exception("Primary source extraction failed.")
            logging.info("Extraction phase completed")
            return primary_data[0]

    async def fetch_data(self, session: aiohttp.ClientSession, url: str) -> Optional[List[Dict[str, Any]]]:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get('states', [])
        except Exception as e:
            logging.error(f"Error fetching data from {url}: {e}")
            return None

    async def join(self, primary_List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        logging.info("Starting join phase")
        enriched_data = []
        async with aiohttp.ClientSession() as session:
            for row in primary_data:
                callsign = row.get('callsign')
                if callsign:
                    callsign_data = await self.fetch_data(session, self.api_urls["src_adsbdb_callsign"].format(callsign=callsign))
                    if callsign_data:
                        row.update(callsign_data.get('response', {}))
                enriched_data.append(row)
        logging.info("Join phase completed")
        return enriched_data

    async def transform(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        logging.info("Starting transform phase")
        transformed_rows = []
        for row in rows:
            row['altitude_category'] = self.categorize_altitude(row)
            row['speed_category'] = self.categorize_speed(row)
            transformed_rows.append(row)
        logging.info("Transform phase completed")
        return transformed_rows

    def categorize_altitude(self, row: Dict[str, Any]) -> str:
        baro_altitude = row.get('baro_altitude')
        on_ground = row.get('on_ground')
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
        return 'Unknown'

    def categorize_speed(self, row: Dict[str, Any]) -> str:
        velocity = row.get('velocity')
        on_ground = row.get('on_ground')
        if velocity is None or on_ground == 'Unknown/Ground':
            return 'Unknown/Ground'
        # Additional speed categorization logic can be added here
        return 'Normal Speed'

    async def load(self, transformed_rows: List[Dict[str, Any]]) -> None:
        logging.info("Starting load phase")
        # Implement the loading logic to the database here
        # For example, using an async database library to insert the data
        logging.info("Load phase completed")

    async def run(self) -> None:
        try:
            primary_data = await self.extract()
            joined_data = await self.join(primary_data)
            transformed_data = await self.transform(joined_data)
            await self.load(transformed_data)
        except Exception as e:
            logging.error(f"ETL process failed: {e}")

if __name__ == "__main__":
    orchestrator = Orchestrator()
    asyncio.run(orchestrator.run())
    with open('.env.example', 'w') as f:
        f.write("DATABASE_URL=postgresql://user:password@localhost:5432/analytics.flight_operations_enriched\n")