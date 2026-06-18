import httpx
import asyncio
import logging
from typing import List, Dict
from httpx import HTTPStatusError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthenticationError(Exception):
    pass

class SrcAdsbdbCallsignExtractor:
    BASE_URL = "https://api.adsbdb.com/v0/callsign/{callsign}"
    
    async def fetch_callsign_data(self, callsign: str) -> List[Dict]:
        attempts = 0
        while attempts < 3:
            async with httpx.AsyncClient() as client:
                try:
                    logger.info(f"Fetching data for callsign: {callsign}")
                    resp = await client.get(
                        self.BASE_URL.format(callsign=callsign),
                        params={},
                        headers={"Accept": "application/json"},
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    logger.info(f"Successfully fetched data for callsign: {callsign}")
                    return data.get('response', [])
                except HTTPStatusError as e:
                    if e.response.status_code == 429:
                        logger.warning("Rate limit exceeded, waiting for 60 seconds before retrying...")
                        await asyncio.sleep(60)
                        attempts += 1
                    elif e.response.status_code in {401, 403}:
                        raise AuthenticationError("Authentication failed, check your credentials.")
                    else:
                        logger.error(f"HTTP error occurred: {e}")
                        break
                except Exception as e:
                    logger.error(f"An error occurred: {e}")
                    break
        logger.error(f"Failed to fetch data for callsign: {callsign} after {attempts} attempts.")
        return []