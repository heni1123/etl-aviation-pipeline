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
        retries = 3
        for attempt in range(retries):
            async with httpx.AsyncClient() as client:
                try:
                    logger.info(f"Fetching data for callsign: {callsign}, attempt: {attempt + 1}")
                    resp = await client.get(
                        self.BASE_URL.format(callsign=callsign),
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
                    elif e.response.status_code in {401, 403}:
                        raise AuthenticationError("Authentication failed, check your credentials.")
                    else:
                        logger.error(f"HTTP error occurred: {e}")
                        raise
                except Exception as e:
                    logger.error(f"An error occurred: {e}")
                    if attempt == retries - 1:
                        raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

    async def extract(self, callsigns: List[str]) -> List[Dict]:
        results = []
        for callsign in callsigns:
            data = await self.fetch_callsign_data(callsign)
            results.extend(data)
        return results