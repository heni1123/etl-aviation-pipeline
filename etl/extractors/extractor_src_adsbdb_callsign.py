import httpx
import asyncio
import logging
from typing import List, Dict

class AuthenticationError(Exception):
    pass

class SrcAdsbdbCallsignExtractor:
    BASE_URL = "https://api.adsbdb.com/v0/callsign/{callsign}"
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    async def fetch_callsign_data(self, callsign: str) -> List[Dict]:
        async with httpx.AsyncClient() as client:
            for attempt in range(3):
                try:
                    self.logger.info(f"Fetching data for callsign: {callsign}, attempt: {attempt + 1}")
                    resp = await client.get(
                        self.BASE_URL.format(callsign=callsign),
                        headers={"Accept": "application/json"},
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    return data.get('response', [])
                except httpx.HTTPStatusError as e:
                    if e.response.status_code in {401, 403}:
                        raise AuthenticationError("Authentication failed") from e
                    elif e.response.status_code == 429:
                        self.logger.warning("Rate limit exceeded, waiting for 60 seconds before retrying.")
                        await asyncio.sleep(60)
                    else:
                        self.logger.error(f"HTTP error occurred: {e}")
                        raise
                except Exception as e:
                    self.logger.error(f"An error occurred: {e}")
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        return []  # Return empty list if all attempts fail

    async def extract(self, callsigns: List[str]) -> List[Dict]:
        results = []
        for callsign in callsigns:
            data = await self.fetch_callsign_data(callsign)
            results.extend(data)
        return results