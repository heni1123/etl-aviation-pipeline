import asyncio
import logging
import os
import time
from typing import List, Dict, Any, Optional
import aiohttp

class Orchestrator:
    def __init__(self) -> None:
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

    async def fetch_rest_countries(self, code: str) -> Optional[Dict[str, Any]]:
        url = f"https://restcountries.com/v3.1/alpha/{code}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    self.logger.warning(f"Failed to fetch country data for {code}")
                    return None
                return await response.json()

    async def extract(self) -> List[Dict[str, Any]]:
        self.logger.info("Starting extraction phase")
        start_time = time.time()
        try:
            states = await self.fetch_opensky_states()
            self.logger.info("Extraction phase completed successfully")
            return states['states']
        except Exception as e:
            self.logger.error(f"Extraction phase failed: {e}")
            raise

    async def join(self, states: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        enriched_states = []
        for state in states:
            callsign_data = await self.fetch_adsbdb_callsign(state['callsign']) if state['callsign'] else None
            country_data = await self.fetch_rest_countries(state['origin_country']) if state['origin_country'] else None
            
            if callsign_data:
                state['airline_name'] = callsign_data['response'].get('airline_name')
                state['airline_iata'] = callsign_data['response'].get('airline_iata')
                state['airline_icao'] = callsign_data['response'].get('airline_icao')
            if country_data:
                state['country_info'] = country_data
            
            enriched_states.append(state)
        return enriched_states

    async def transform(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
                "baro_altitude": row['baro_altitude'],
                "on_ground": row['on_ground'],
                "velocity": row['velocity'],
                "true_track": row['true_track'],
                "vertical_rate": row['vertical_rate'],
                "geo_altitude": row['geo_altitude'],
                "squawk": row['squawk'],
                "spi": row['spi'],
                "callsign_iata": row.get('callsign_iata'),
                "airline_name": row.get('airline_name'),
                "airline_iata": row.get('airline_iata'),
                "airline_icao": row.get('airline_icao'),
                "dep_airport_iata": row.get('dep_airport_iata'),
            }
            transformed_rows.append(transformed_row)
        return transformed_rows

    async def load(self, transformed_rows: List[Dict[str, Any]]) -> None:
        # Here you would implement the logic to load the data into the PostgreSQL database
        # For example, using an async database library like asyncpg
        pass

    async def run(self) -> None:
        try:
            states = await self.extract()
            enriched_states = await self.join(states)
            transformed_rows = await self.transform(enriched_states)
            await self.load(transformed_rows)
        except Exception as e:
            self.logger.error(f"ETL process failed: {e}")

if __name__ == "__main__":
    orchestrator = Orchestrator()
    asyncio.run(orchestrator.run())