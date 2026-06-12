import httpx
import asyncio
import logging
from typing import List, Dict
from httpx import HTTPStatusError

class AuthenticationError(Exception):
    pass

class SrcAdsbdbCallsignExtractor:
    BASE_URL = "https://api.adsbdb.com/v0/callsign/{callsign}"
    
    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO)
    
    async def fetch_callsign_data(self, callsign: str) -> Dict:
        async with httpx.AsyncClient() as client:
            for attempt in range(3):
                try:
                    logging.info(f"Fetching data for callsign: {callsign}, attempt: {attempt + 1}")
                    resp = await client.get(
                        self.BASE_URL.format(callsign=callsign),
                        headers={"Accept": "application/json"},
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    return data['response']
                except HTTPStatusError as e:
                    if e.response.status_code == 429:
                        logging.warning("Rate limit exceeded, waiting for 60 seconds before retrying.")
                        await asyncio.sleep(60)
                    elif e.response.status_code in {401, 403}:
                        raise AuthenticationError("Authentication failed.")
                    else:
                        logging.error(f"HTTP error occurred: {e}")
                        raise
                except Exception as e:
                    logging.error(f"An error occurred: {e}")
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        return {}

    async def extract(self, callsigns: List[str]) -> List[Dict]:
        results = []
        for callsign in callsigns:
            data = await self.fetch_callsign_data(callsign)
            results.append(data)
        return results