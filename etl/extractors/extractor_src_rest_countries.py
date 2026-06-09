import httpx
import asyncio
import logging
from typing import List, Dict

class AuthenticationError(Exception):
    pass

class SrcRestCountriesExtractor:
    BASE_URL = "https://restcountries.com/v3.1/alpha/{origin_country}"
    HEADERS = {"Accept": "application/json"}
    RETRY_ATTEMPTS = 3
    RATE_LIMIT_WAIT = 60

    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO)

    async def fetch_country_data(self, origin_country: str) -> Dict:
        async with httpx.AsyncClient() as client:
            for attempt in range(self.RETRY_ATTEMPTS):
                try:
                    resp = await client.get(
                        self.BASE_URL.format(origin_country=origin_country),
                        params={"fields": "name,cca2,region,subregion,population,area,capital,continents"},
                        headers=self.HEADERS,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    logging.info(f"Fetched data for {origin_country} with latency {resp.elapsed.total_seconds() * 1000:.2f} ms")
                    return data
                except httpx.HTTPStatusError as e:
                    if e.response.status_code in {401, 403}:
                        raise AuthenticationError("Authentication failed") from e
                    elif e.response.status_code == 429:
                        logging.warning("Rate limit exceeded, waiting for 60 seconds before retrying...")
                        await asyncio.sleep(self.RATE_LIMIT_WAIT)
                    else:
                        logging.error(f"HTTP error occurred: {e}")
                        raise
                except Exception as e:
                    logging.error(f"An error occurred: {e}")
                    raise
            logging.error("Max retry attempts reached")
            return {}

    async def extract(self, origin_countries: List[str]) -> List[Dict]:
        results = []
        for country in origin_countries:
            country_data = await self.fetch_country_data(country)
            if country_data:
                results.append(country_data)
        return results