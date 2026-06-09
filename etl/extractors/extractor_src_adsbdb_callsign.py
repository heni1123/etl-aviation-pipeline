import httpx
import asyncio
import logging
from typing import List, Dict, Any
from httpx import HTTPStatusError

class AuthenticationError(Exception):
    pass

class SrcAdsbdbCallsignExtractor:
    def __init__(self) -> None:
        self.url_template = "https://api.adsbdb.com/v0/callsign/{callsign}"
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    async def fetch_callsign_data(self, callsign: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            for attempt in range(3):
                try:
                    self.logger.info(f"Fetching data for callsign: {callsign}")
                    resp = await client.get(
                        self.url_template.format(callsign=callsign),
                        headers={"Accept": "application/json"},
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    return data['response']
                except HTTPStatusError as e:
                    if e.response.status_code == 429:
                        self.logger.warning("Rate limit exceeded, waiting 60 seconds before retrying...")
                        await asyncio.sleep(60)
                    elif e.response.status_code in {401, 403}:
                        raise AuthenticationError("Authentication failed, check your credentials.")
                    else:
                        self.logger.error(f"HTTP error occurred: {e}")
                        raise
                except Exception as e:
                    self.logger.error(f"An error occurred: {e}")
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

    async def extract(self, callsigns: List[str]) -> List[Dict[str, Any]]:
        results = []
        for callsign in callsigns:
            try:
                data = await self.fetch_callsign_data(callsign)
                results.append(data)
            except Exception as e:
                self.logger.error(f"Failed to extract data for callsign {callsign}: {e}")
        return results

# Example usage:
# extractor = SrcAdsbdbCallsignExtractor()
# asyncio.run(extractor.extract(['CALLSIGN1', 'CALLSIGN2']))