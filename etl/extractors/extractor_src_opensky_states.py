import httpx
import asyncio
import logging
from typing import List, Dict

class AuthenticationError(Exception):
    pass

class SrcOpenskyStatesExtractor:
    def __init__(self, url: str, params: Dict[str, str]):
        self.url = url
        self.params = params
        self.logger = logging.getLogger(__name__)

    async def fetch_data(self) -> List[Dict]:
        retries = 3
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient() as client:
                    self.logger.info("Sending request to %s with params %s", self.url, self.params)
                    resp = await client.get(self.url, params=self.params, headers={"Accept": "application/json"})
                    resp.raise_for_status()
                    data = resp.json()
                    return data['states']
            except httpx.HTTPStatusError as e:
                if e.response.status_code in {401, 403}:
                    raise AuthenticationError("Authentication failed") from e
                elif e.response.status_code == 429:
                    self.logger.warning("Rate limit exceeded, waiting for 60 seconds before retrying...")
                    await asyncio.sleep(60)
                else:
                    self.logger.error("HTTP error occurred: %s", e)
                    raise
            except Exception as e:
                self.logger.error("An error occurred: %s", e)
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
        return []  # Return an empty list if all retries fail

# Example usage:
# extractor = SrcOpenskyStatesExtractor("https://opensky-network.org/api/states/all", {
#     "lamin": "28.0",
#     "lomin": "-10.0",
#     "lamax": "47.0",
#     "lomax": "37.0"
# })
# asyncio.run(extractor.fetch_data())