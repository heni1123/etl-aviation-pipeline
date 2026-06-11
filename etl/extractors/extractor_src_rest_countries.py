import httpx
import asyncio
import logging
from typing import List, Dict

class AuthenticationError(Exception):
    pass

class SrcRestCountriesExtractor:
    def __init__(self, codes: List[str]):
        self.codes = codes
        self.url = "https://restcountries.com/v3.1/alpha/{code}"
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    async def fetch_country_data(self, code: str) -> Dict:
        async with httpx.AsyncClient() as client:
            for attempt in range(3):
                try:
                    self.logger.info(f"Fetching data for code: {code}")
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
                        break
                except httpx.RequestError as e:
                    self.logger.error(f"Request error occurred: {e}")
                    break
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        return {}

    async def extract(self) -> List[Dict]:
        results = []
        for code in self.codes:
            country_data = await self.fetch_country_data(code)
            if country_data:
                results.append(country_data)
        return results

async def main():
    extractor = SrcRestCountriesExtractor(codes=["FR", "DE", "US"])
    country_data = await extractor.extract()
    print(country_data)

if __name__ == "__main__":
    asyncio.run(main())