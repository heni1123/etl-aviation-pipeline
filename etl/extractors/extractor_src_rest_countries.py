import httpx
import asyncio
import logging
from typing import List, Dict

class AuthenticationError(Exception):
    pass

class SrcRestCountriesExtractor:
    BASE_URL = "https://restcountries.com/v3.1/alpha/{origin_country}"
    HEADERS = {"Accept": "application/json"}
    PARAMS = {"fields": "name,cca2,region,subregion,population,area,capital,continents"}
    MAX_RETRIES = 3

    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO)

    async def fetch_country_data(self, origin_country: str) -> List[Dict]:
        async with httpx.AsyncClient() as client:
            for attempt in range(self.MAX_RETRIES):
                try:
                    logging.info(f"Fetching data for {origin_country}, attempt {attempt + 1}")
                    resp = await client.get(
                        self.BASE_URL.format(origin_country=origin_country),
                        params=self.PARAMS,
                        headers=self.HEADERS,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    return data.get('data', [])
                except httpx.HTTPStatusError as e:
                    if e.response.status_code in {401, 403}:
                        raise AuthenticationError("Authentication failed") from e
                    elif e.response.status_code == 429:
                        logging.warning("Rate limit exceeded, waiting for 60 seconds before retrying...")
                        await asyncio.sleep(60)
                    else:
                        logging.error(f"HTTP error occurred: {e}")
                        break
                except Exception as e:
                    logging.error(f"An error occurred: {e}")
                    break
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        return []

    async def extract(self, origin_countries: List[str]) -> List[Dict]:
        results = []
        for country in origin_countries:
            country_data = await self.fetch_country_data(country)
            results.extend(country_data)
        return results