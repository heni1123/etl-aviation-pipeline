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
    BASE_URL = "https://restcountries.com/v3.1/alpha/{origin_country}"
    HEADERS = {"Accept": "application/json"}
    RETRY_ATTEMPTS = 3
    RATE_LIMIT_WAIT = 60

    async def fetch_country_data(self, origin_country: str) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            for attempt in range(self.RETRY_ATTEMPTS):
                try:
                    logger.info(f"Fetching data for country: {origin_country}, attempt: {attempt + 1}")
                    resp = await client.get(
                        self.BASE_URL.format(origin_country=origin_country),
                        params={"fields": "name,cca2,region,subregion,population,area,capital,continents"},
                        headers=self.HEADERS,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    logger.info(f"Successfully fetched data for {origin_country}")
                    return data
                except HTTPStatusError as e:
                    if e.response.status_code == 429:
                        logger.warning("Rate limit exceeded, waiting for 60 seconds before retrying...")
                        await asyncio.sleep(self.RATE_LIMIT_WAIT)
                    elif e.response.status_code in {401, 403}:
                        raise AuthenticationError("Authentication failed, check your credentials.")
                    else:
                        logger.error(f"HTTP error occurred: {e}")
                        raise
                except Exception as e:
                    logger.error(f"An error occurred: {e}")
                    raise
        logger.error("Max retry attempts reached, failed to fetch data.")
        return []  # Return an empty list if all attempts fail

    async def extract(self, origin_countries: List[str]) -> List[Dict[str, Any]]:
        results = []
        for country in origin_countries:
            country_data = await self.fetch_country_data(country)
            results.append(country_data)
        return results