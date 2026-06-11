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
        self.logger = self.setup_logging()

    def setup_logging(self) -> logging.Logger:
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)

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
                self.fetch(session, self.api_urls["src_adsbdb_callsign"].format(callsign='')),
                self.fetch(session, self.api_urls["src_rest_countries"].format(origin_country=''))
            )
            if primary_data is None:
                self.logger.critical("Primary source extraction failed, aborting ETL process.")
                raise Exception("Primary source extraction failed.")
            return {
                "primary_data": primary_data,
                "callsign_data": callsign_data,
                "country_data": country_data
            }

    async def join(self, Dict[str, Any]) -> List[Dict[str, Any]]:
        primary_data = data["primary_data"]["states"]
        enriched_data = []
        for row in primary_data:
            callsign_info = data["callsign_data"] if row[1] else None
            country_info = data["country_data"] if row[2] else None
            enriched_row = {
                "icao24": row[0],
                "callsign": row[1],
                "origin_country": row[2],
                "time_position": row[3],
                "last_contact": row[4],
                "longitude": row[5],
                "latitude": row[6],
                "baro_altitude": row[7],
                "on_ground": row[8],
                "velocity": row[9],
                "true_track": row[10],
                "vertical_rate": row[11],
                "geo_altitude": row[12],
                "squawk": row[13],
                "spi": row[14],
                "callsign_iata": callsign_info.get('iata', None) if callsign_info else None,
                "airline_name": callsign_info.get('airline', None) if callsign_info else None,
                "airline_iata": callsign_info.get('iata', None) if callsign_info else None,
                "airline_icao": callsign_info.get('icao', None) if callsign_info else None,
                "dep_airport_iata": country_info.get('iata', None) if country_info else None,
                # Add other fields as necessary
            }
            enriched_data.append(enriched_row)
        return enriched_data

    async def transform(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for row in rows:
            row['altitude_category'] = self.categorize_altitude(row.get('baro_altitude'), row.get('on_ground'))
            row['speed_category'] = self.categorize_speed(row.get('velocity'), row.get('on_ground'))
        return rows

    def categorize_altitude(self, baro_altitude: Optional[float], on_ground: Optional[bool]) -> str:
        if baro_altitude is None or on_ground:
            return 'Ground'
        elif 0 < baro_altitude <= 3000:
            return 'Low Altitude'
        elif 3000 < baro_altitude <= 7500:
            return 'Mid Altitude'
        elif 7500 < baro_altitude <= 12500:
            return 'Cruise Altitude'
        else:
            return 'High Altitude'

    def categorize_speed(self, velocity: Optional[float], on_ground: Optional[bool]) -> str:
        if velocity is None or on_ground:
            return 'Unknown/Ground'
        elif velocity < 100:
            return 'Slow'
        elif velocity < 300:
            return 'Medium'
        else:
            return 'Fast'

    async def load(self, transformed_rows: List[Dict[str, Any]]) -> None:
        # Implement the logic to load data into the PostgreSQL database
        pass

    async def run(self) -> None:
        self.logger.info("ETL process started.")
        try:
            extraction_start = asyncio.get_event_loop().time()
            data = await self.extract()
            extraction_duration = asyncio.get_event_loop().time() - extraction_start
            self.logger.info(f"Extraction completed in {extraction_duration:.2f} seconds.")

            joining_start = asyncio.get_event_loop().time()
            joined_data = await self.join(data)
            joining_duration = asyncio.get_event_loop().time() - joining_start
            self.logger.info(f"Joining completed in {joining_duration:.2f} seconds.")

            transformation_start = asyncio.get_event_loop().time()
            transformed_data = await self.transform(joined_data)
            transformation_duration = asyncio.get_event_loop().time() - transformation_start
            self.logger.info(f"Transformation completed in {transformation_duration:.2f} seconds.")

            loading_start = asyncio.get_event_loop().time()
            await self.load(transformed_data)
            loading_duration = asyncio.get_event_loop().time() - loading_start
            self.logger.info(f"Loading completed in {loading_duration:.2f} seconds.")

        except Exception as e:
            self.logger.error(f"ETL process failed: {e}")
        finally:
            self.logger.info("ETL process finished.")

if __name__ == "__main__":
    orchestrator = Orchestrator()
    asyncio.run(orchestrator.run())
    with open('.env.example', 'w') as f:
        f.write("DATABASE_URL=postgresql://user:password@localhost:5432/analytics.flight_operations_enriched\n")