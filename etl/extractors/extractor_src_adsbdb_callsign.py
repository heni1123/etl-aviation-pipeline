import httpx
import asyncio
import logging
from typing import List, Dict

class AuthenticationError(Exception):
    pass

class SrcAdsbdbCallsignExtractor:
    def __init__(self, callsigns: List[str]) -> None:
        self.callsigns = callsigns
        self.url = "https://api.adsbdb.com/v0/callsign/{callsign}"
        self.logger = logging.getLogger(__name__)

    async def fetch_callsign_data(self, callsign: str) -> Dict:
        async with httpx.AsyncClient() as client:
            for attempt in range(3):
                try:
                    self.logger.info(f"Fetching data for callsign: {callsign}")
                    resp = await client.get(
                        self.url.format(callsign=callsign),
                        params={"callsign": callsign},
                        headers={"Accept": "application/json"},
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    return data['response']
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

    async def extract(self) -> List[Dict]:
        results = []
        for callsign in self.callsigns:
            try:
                data = await self.fetch_callsign_data(callsign)
                results.append(data)
            except Exception as e:
                self.logger.error(f"Failed to extract data for callsign {callsign}: {e}")
        return results

# Example usage:
# extractor = SrcAdsbdbCallsignExtractor(callsigns=["ABC123", "DEF456"])
# asyncio.run(extractor.extract())