import httpx
import asyncio
import logging
from typing import List, Dict, Any
from httpx import HTTPStatusError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthenticationError(Exception):
    pass

class SrcAdsbdbCallsignExtractor:
    def __init__(self, callsigns: List[str]) -> None:
        self.callsigns = callsigns
        self.url = "https://api.adsbdb.com/v0/callsign/{callsign}"

    async def fetch_callsign_data(self, callsign: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            for attempt in range(3):
                try:
                    logger.info(f"Fetching data for callsign: {callsign}")
                    resp = await client.get(
                        self.url.format(callsign=callsign),
                        headers={"Accept": "application/json"},
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    return data['response']
                except HTTPStatusError as e:
                    if e.response.status_code in {401, 403}:
                        raise AuthenticationError("Authentication failed") from e
                    elif e.response.status_code == 429:
                        logger.warning("Rate limit exceeded, waiting for 60 seconds before retrying...")
                        await asyncio.sleep(60)
                    else:
                        logger.error(f"HTTP error occurred: {e}")
                        raise
                except Exception as e:
                    logger.error(f"An error occurred: {e}")
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        return {}

    async def extract(self) -> List[Dict[str, Any]]:
        results = []
        for callsign in self.callsigns:
            data = await self.fetch_callsign_data(callsign)
            if data:
                results.append(data)
        return results

async def main():
    extractor = SrcAdsbdbCallsignExtractor(callsigns=["AAL123", "DAL456"])
    data = await extractor.extract()
    print(data)

if __name__ == "__main__":
    asyncio.run(main())