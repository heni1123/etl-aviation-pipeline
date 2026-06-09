import httpx
import asyncio
import logging
from typing import List, Dict

class AuthenticationError(Exception):
    pass

class SrcRestCountriesExtractor:
    def __init__(self, codes: List[str]) -> None:
        self.codes = codes
        self.url = "https://restcountries.com/v3.1/alpha/{code}"
        self.logger = logging.getLogger(__name__)

    async def fetch_country_data(self, code: str) -> Dict:
        async with httpx.AsyncClient() as client:
            for attempt in range(3):
                try:
                    self.logger.info(f"Fetching data for country code: {code}")
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
        tasks = [self.fetch_country_data(code) for code in self.codes]
        results = await asyncio.gather(*tasks)
        return results

# Example usage:
# extractor = SrcRestCountriesExtractor(codes=["US", "FR", "DE"])
# asyncio.run(extractor.extract())