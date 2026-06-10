import httpx
import asyncio
import logging
from typing import List, Dict

class AuthenticationError(Exception):
    pass

class SrcRestCountriesExtractor:
    def __init__(self) -> None:
        self.url = "https://restcountries.com/v3.1/alpha/{code}"
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    async def fetch_country_data(self, code: str) -> Dict:
        async with httpx.AsyncClient() as client:
            for attempt in range(3):
                try:
                    self.logger.info(f"Fetching data for ISO code: {code}")
                    resp = await client.get(
                        self.url.format(code=code),
                        headers={"Accept": "application/json"},
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    return data
                except httpx.HTTPStatusError as e:
                    if e.response.status_code in {401, 403}:
                        raise AuthenticationError("Authentication failed") from e
                    elif e.response.status_code == 429:
                        self.logger.warning("Rate limit exceeded, waiting 60 seconds before retrying...")
                        await asyncio.sleep(60)
                    else:
                        self.logger.error(f"HTTP error occurred: {e}")
                        raise
                except Exception as e:
                    self.logger.error(f"An error occurred: {e}")
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        return {}

    async def extract(self, codes: List[str]) -> List[Dict]:
        results = []
        for code in codes:
            data = await self.fetch_country_data(code)
            results.append(data)
        return results

# Example usage:
# extractor = SrcRestCountriesExtractor()
# asyncio.run(extractor.extract(['FR', 'US']))