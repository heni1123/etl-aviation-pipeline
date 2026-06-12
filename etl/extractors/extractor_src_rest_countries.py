import httpx
import asyncio
import logging
from typing import List, Dict, Any
from httpx import HTTPStatusError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthenticationError(Exception):
    pass

class SrcRestCountriesExtractor:
    def __init__(self, codes: List[str]) -> None:
        self.codes = codes
        self.url = "https://restcountries.com/v3.1/alpha/{code}"

    async def fetch_country_data(self, code: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            for attempt in range(3):
                try:
                    logger.info(f"Fetching data for code: {code}, attempt: {attempt + 1}")
                    resp = await client.get(
                        self.url.format(code=code),
                        headers={"Accept": "application/json"},
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    logger.info(f"Successfully fetched data for code: {code}")
                    return data
                except HTTPStatusError as e:
                    if e.response.status_code == 429:
                        logger.warning("Rate limit exceeded, waiting for 60 seconds before retrying...")
                        await asyncio.sleep(60)
                    elif e.response.status_code in {401, 403}:
                        raise AuthenticationError("Authentication failed, check your credentials.")
                    else:
                        logger.error(f"HTTP error occurred: {e}")
                        raise
                except Exception as e:
                    logger.error(f"An error occurred: {e}")
                    raise
            logger.error(f"Failed to fetch data for code: {code} after 3 attempts")
            return {}

    async def extract(self) -> List[Dict[str, Any]]:
        results = []
        for code in self.codes:
            data = await self.fetch_country_data(code)
            results.append(data)
        return results

async def main():
    extractor = SrcRestCountriesExtractor(codes=["FR", "US", "DE"])
    country_data = await extractor.extract()
    print(country_data)

if __name__ == "__main__":
    asyncio.run(main())