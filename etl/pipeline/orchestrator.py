import asyncio
import logging
import os
from typing import List, Dict, Any, Optional
import aiohttp
from dotenv import dotenv_values

class Orchestrator:
    def __init__(self) -> None:
        self.api_urls = {
            "src_opensky_states": "https://opensky-network.org/api/states/all",
            "src_adsbdb_callsign": "https://api.adsbdb.com/v0/callsign/{callsign}",
            "src_rest_countries": "https://restcountries.com/v3.1/alpha/{origin_country}"
        }
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    async def fetch(self, session: aiohttp.ClientSession, url: str) -> Optional[Dict[str, Any]]:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            self.logger.error(f"Error fetching data from {url}: {e}")
            return None

    async def extract(self) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            primary_data, callsign_data, country_data = await asyncio.gather(
                self.fetch(session, self.api_urls["src_opensky_states"]),
                self.fetch(session, self.api_urls["src_adsbdb_callsign"].format(callsign="")),
                self.fetch(session, self.api_urls["src_rest_countries"].format(origin_country=""))
            )
            if primary_data is None:
                raise RuntimeError("Primary source extraction failed.")
            return {
                "primary_data": primary_data,
                "callsign_data": callsign_data,
                "country_data": country_data
            }

    async def join(self, Dict[str, Any]) -> List[Dict[str, Any]]:
        primary_data = data["primary_data"]["states"]
        enriched_data = []
        for row in primary_data:
            callsign_info = await self.fetch_callsign_info(row[1])  # Assuming callsign is at index 1
            country_info = await self.fetch_country_info(row[2])  # Assuming origin_country is at index 2
            enriched_row = {**row, **callsign_info, **country_info}
            enriched_data.append(enriched_row)
        return enriched_data

    async def fetch_callsign_info(self, callsign: str) -> Dict[str, Any]:
        if callsign:
            url = self.api_urls["src_adsbdb_callsign"].format(callsign=callsign)
            return await self.fetch(aiohttp.ClientSession(), url) or {}
        return {}

    async def fetch_country_info(self, origin_country: str) -> Dict[str, Any]:
        if origin_country:
            url = self.api_urls["src_rest_countries"].format(origin_country=origin_country)
            return await self.fetch(aiohttp.ClientSession(), url) or {}
        return {}

    async def transform(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        transformed_rows = []
        for row in rows:
            transformed_row = self.apply_business_rules(row)
            transformed_rows.append(transformed_row)
        return transformed_rows

    def apply_business_rules(self, row: Dict[str, Any]) -> Dict[str, Any]:
        row['altitude_category'] = self.categorize_altitude(row.get('baro_altitude'), row.get('on_ground'))
        row['speed_category'] = self.categorize_speed(row.get('velocity'), row.get('on_ground'))
        return row

    def categorize_altitude(self, baro_altitude: Optional[float], on_ground: Optional[bool]) -> str:
        if baro_altitude is None or on_ground:
            return 'Ground'
        elif baro_altitude <= 3000:
            return 'Low Altitude'
        elif baro_altitude <= 7500:
            return 'Mid Altitude'
        elif baro_altitude <= 12500:
            return 'Cruise Altitude'
        else:
            return 'High Altitude'

    def categorize_speed(self, velocity: Optional[float], on_ground: Optional[bool]) -> str:
        if velocity is None or on_ground:
            return 'Unknown/Ground'
        elif velocity <= 80:
            return 'Taxi/Slow'
        elif velocity <= 150:
            return 'Approach'
        elif velocity <= 230:
            return 'Climb/Descent'
        else:
            return 'Cruise'

    async def load(self, transformed_rows: List[Dict[str, Any]]) -> None:
        # Implement the loading logic to the database here
        pass

    async def run(self) -> None:
        self.logger.info("ETL process started.")
        try:
            data = await self.extract()
            enriched_data = await self.join(data)
            transformed_rows = await self.transform(enriched_data)
            await self.load(transformed_rows)
        except Exception as e:
            self.logger.error(f"ETL process failed: {e}")
        finally:
            self.logger.info("ETL process completed.")

if __name__ == "__main__":
    orchestrator = Orchestrator()
    asyncio.run(orchestrator.run())
    with open('.env.example', 'w') as f:
        f.write("API_SRC_OPENSKY=https://opensky-network.org/api/states/all\n")
        f.write("API_SRC_ADSBDDB=https://api.adsbdb.com/v0/callsign/{callsign}\n")
        f.write("API_SRC_REST_COUNTRIES=https://restcountries.com/v3.1/alpha/{origin_country}\n")