import asyncio
import logging
import os
from typing import List, Dict, Any, Optional
import aiohttp
from dotenv import dotenv_values

class Orchestrator:
    def __init__(self):
        self.api_urls = {
            "src_opensky_states": "https://opensky-network.org/api/states/all",
            "src_adsbdb_callsign": "https://api.adsbdb.com/v0/callsign/{callsign}",
            "src_rest_countries": "https://restcountries.com/v3.1/alpha/{origin_country}"
        }
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    async def extract(self) -> List[Dict[str, Any]]:
        self.logger.info("Starting extraction phase")
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.api_urls["src_opensky_states"]) as response:
                    response.raise_for_status()
                    opensky_data = await response.json()
                    states = opensky_data.get('states', [])
                    self.logger.info("Extraction completed successfully")
                    return states
            except Exception as e:
                self.logger.error(f"Error during extraction: {e}")
                raise

    async def enrich_callsign(self, states: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.logger.info("Starting callsign enrichment phase")
        async with aiohttp.ClientSession() as session:
            enriched_states = []
            for state in states:
                callsign = state.get('callsign')
                if callsign:
                    try:
                        async with session.get(self.api_urls["src_adsbdb_callsign"].format(callsign=callsign)) as response:
                            response.raise_for_status()
                            callsign_data = await response.json()
                            state.update(callsign_data.get('response', {}))
                    except Exception as e:
                        self.logger.warning(f"Enrichment failed for callsign {callsign}: {e}")
                enriched_states.append(state)
            self.logger.info("Callsight enrichment completed")
            return enriched_states

    async def enrich_country(self, states: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.logger.info("Starting country enrichment phase")
        async with aiohttp.ClientSession() as session:
            enriched_states = []
            for state in states:
                origin_country = state.get('origin_country')
                if origin_country:
                    try:
                        async with session.get(self.api_urls["src_rest_countries"].format(origin_country=origin_country)) as response:
                            response.raise_for_status()
                            country_data = await response.json()
                            state.update(country_data)
                    except Exception as e:
                        self.logger.warning(f"Enrichment failed for country {origin_country}: {e}")
                enriched_states.append(state)
            self.logger.info("Country enrichment completed")
            return enriched_states

    async def transform(self, states: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.logger.info("Starting transformation phase")
        transformed_rows = []
        for row in states:
            transformed_row = {
                "icao24": row.get("icao24"),
                "callsign": row.get("callsign"),
                "origin_country": row.get("origin_country"),
                "time_position": row.get("time"),
                "last_contact": row.get("last_contact"),
                "longitude": row.get("longitude"),
                "latitude": row.get("latitude"),
                "baro_altitude": row.get("baro_altitude"),
                "on_ground": row.get("on_ground"),
                "velocity": row.get("velocity"),
                "true_track": row.get("true_track"),
                "vertical_rate": row.get("vertical_rate"),
                "geo_altitude": row.get("geo_altitude"),
                "squawk": row.get("squawk"),
                "spi": row.get("spi"),
                "callsign_iata": row.get("callsign_iata"),
                "airline_name": row.get("airline_name"),
                "airline_iata": row.get("airline_iata"),
                "airline_icao": row.get("airline_icao"),
                "dep_airport_iata": row.get("dep_airport_iata"),
                "altitude_category": self.categorize_altitude(row),
                "speed_category": self.categorize_speed(row)
            }
            transformed_rows.append(transformed_row)
        self.logger.info("Transformation completed")
        return transformed_rows

    def categorize_altitude(self, row: Dict[str, Any]) -> Optional[str]:
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
        return None

    def categorize_speed(self, row: Dict[str, Any]) -> Optional[str]:
        velocity = row.get('velocity')
        on_ground = row.get('on_ground')
        if velocity is None or on_ground == 'Unknown/Ground':
            return 'Unknown/Ground'
        elif velocity < 100:
            return 'Slow'
        elif 100 <= velocity < 300:
            return 'Normal'
        elif velocity >= 300:
            return 'Fast'
        return None

    async def load(self, transformed_rows: List[Dict[str, Any]]) -> None:
        self.logger.info("Starting load phase")
        # Here you would implement the logic to load the transformed_rows into the database
        # For example, using an async database library like asyncpg
        self.logger.info("Load phase completed")

    async def run(self) -> None:
        try:
            states = await self.extract()
            enriched_callsign_states = await self.enrich_callsign(states)
            enriched_country_states = await self.enrich_country(enriched_callsign_states)
            transformed_rows = await self.transform(enriched_country_states)
            await self.load(transformed_rows)
        except Exception as e:
            self.logger.error(f"ETL process failed: {e}")

if __name__ == "__main__":
    orchestrator = Orchestrator()
    asyncio.run(orchestrator.run())
    with open('.env.example', 'w') as f:
        f.write("API_URL_OPENSKY=https://opensky-network.org/api/states/all\n")
        f.write("API_URL_ADSBDDB=https://api.adsbdb.com/v0/callsign/{callsign}\n")
        f.write("API_URL_REST_COUNTRIES=https://restcountries.com/v3.1/alpha/{origin_country}\n")