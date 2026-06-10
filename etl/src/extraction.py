import aiohttp
import asyncio
import logging
import time
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataExtractor:
    BASE_OPENSKY_URL = "https://opensky-network.org/api/states/all"
    BASE_ADSBDB_URL = "https://adsbdb.com/api/aircraft/"

    async def fetch_opensky_data(self) -> List[Dict]:
        retries = 5
        for attempt in range(retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.BASE_OPENSKY_URL) as response:
                        response.raise_for_status()
                        data = await response.json()
                        logger.info("Successfully fetched OpenSky data.")
                        return data.get('states', [])
            except aiohttp.ClientError as e:
                logger.error(f"Error fetching OpenSky {e}")
                if attempt < retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.critical("Max retries reached for OpenSky data.")
                    raise

    async def fetch_adsb_data(self, callsign: str) -> Dict:
        retries = 5
        for attempt in range(retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.BASE_ADSBDB_URL}{callsign}") as response:
                        response.raise_for_status()
                        data = await response.json()
                        logger.info(f"Successfully fetched ADSB data for callsign: {callsign}.")
                        return data
            except aiohttp.ClientError as e:
                logger.error(f"Error fetching ADSB data for callsign {callsign}: {e}")
                if attempt < retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.critical(f"Max retries reached for ADSB data for callsign {callsign}.")
                    raise