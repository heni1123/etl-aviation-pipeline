import httpx
import asyncio
import logging
from typing import List, Dict
from httpx import HTTPStatusError

class AuthenticationError(Exception):
    pass

class SrcAdsbdbCallsignExtractor:
    def __init__(self) -> None:
        self.url = "https://api.adsbdb.com/v0/callsign/{callsign}"
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    async def fetch_callsign_data(self, callsign: str) -> List[Dict]:
        attempts = 0
        while attempts < 3:
            try:
                async with httpx.AsyncClient() as client:
                    self.logger.info(f"Fetching data for callsign: {callsign}")
                    resp = await client.get(
                        self.url.format(callsign=callsign),
                        params={"callsign": callsign},
                        headers={"Accept": "application/json"},
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    self.logger.info(f"Successfully fetched data for callsign: {callsign}")
                    return data.get('response', [])
            except HTTPStatusError as e:
                if e.response.status_code == 429:
                    self.logger.warning("Rate limit exceeded, waiting for 60 seconds before retrying.")
                    await asyncio.sleep(60)
                elif e.response.status_code in {401, 403}:
                    raise AuthenticationError("Authentication failed, check your credentials.")
                else:
                    self.logger.error(f"HTTP error occurred: {e}")
                    raise
            except Exception as e:
                self.logger.error(f"An error occurred: {e}")
                raise
            attempts += 1
            await asyncio.sleep(2 ** attempts)  # Exponential backoff
        self.logger.error("Max retries exceeded.")
        return []