import httpx
import asyncio
import logging
from typing import List, Dict, Any

class AuthenticationError(Exception):
    pass

class SrcAdsbdbCallsignExtractor:
    def __init__(self) -> None:
        self.url = "https://api.adsbdb.com/v0/callsign/{callsign}"
        self.logger = logging.getLogger(__name__)

    async def fetch_callsign_data(self, callsign: str) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            for attempt in range(3):
                try:
                    self.logger.info(f"Fetching data for callsign: {callsign}")
                    resp = await client.get(
                        self.url.format(callsign=callsign),
                        params={"callsign": callsign.strip().upper()},
                        headers={"Accept": "application/json"},
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    self.logger.info(f"Successfully fetched data for callsign: {callsign}")
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

    async def extract(self, callsigns: List[str]) -> List[Dict[str, Any]]:
        results = []
        for callsign in callsigns:
            data = await self.fetch_callsign_data(callsign)
            results.extend(data)
        return results