import asyncio
import logging
import os
from typing import List, Dict, Any
import aiohttp
from datetime import datetime
from transformer import Transformer
from loader import Loader

logging.basicConfig(level=logging.INFO)

class Orchestrator:
    def __init__(self, db_url: str):
        self.db_url = db_url

    async def fetch_opensky_states(self) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://opensky-network.org/api/states/all") as response:
                response.raise_for_status()
                data = await response.json()
                return data['states']

    async def fetch_adsbdb_callsign(self, callsign: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.adsbdb.com/v0/callsign/{callsign}") as response:
                response.raise_for_status()
                return await response.json()

    async def fetch_rest_countries(self, code: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://restcountries.com/v3.1/alpha/{code}") as response:
                response.raise_for_status()
                return await response.json()

    async def extract(self) -> List[Dict[str, Any]]:
        logging.info("Starting extraction phase")
        start_time = datetime.now()
        try:
            opensky_data = await self.fetch_opensky_states()
            logging.info("Extraction phase completed successfully")
            return opensky_data
        except Exception as e:
            logging.error(f"Extraction failed: {e}")
            raise

    async def enrich(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        enriched_rows = []
        for row in rows:
            try:
                callsign_data = await self.fetch_adsbdb_callsign(row['callsign'])
                country_data = await self.fetch_rest_countries(row['origin_country'])
                row['airline_name'] = callsign_data.get('response', {}).get('airline_name')
                row['airline_iata'] = callsign_data.get('response', {}).get('airline_iata')
                row['airline_icao'] = callsign_data.get('response', {}).get('airline_icao')
                row['country_name'] = country_data.get('data', {}).get('name')
                enriched_rows.append(row)
            except Exception as e:
                logging.warning(f"Enrichment failed for row {row}: {e}")
                enriched_rows.append(row)  # Append row with NULL fields
        return enriched_rows

    async def transform(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        logging.info("Starting transformation phase")
        transformed_rows = Transformer.transform(rows)
        logging.info("Transformation phase completed successfully")
        return transformed_rows

    async def load(self, rows: List[Dict[str, Any]]) -> None:
        logging.info("Starting load phase")
        await Loader.load(rows, self.db_url)
        logging.info("Load phase completed successfully")

    async def run(self) -> None:
        try:
            extracted_rows = await self.extract()
            enriched_rows = await self.enrich(extracted_rows)
            transformed_rows = await self.transform(enriched_rows)
            await self.load(transformed_rows)
        except Exception as e:
            logging.error(f"ETL process failed: {e}")

if __name__ == "__main__":
    db_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/analytics.cible")
    orchestrator = Orchestrator(db_url)
    asyncio.run(orchestrator.run())