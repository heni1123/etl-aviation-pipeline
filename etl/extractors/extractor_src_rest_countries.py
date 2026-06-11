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
    PARAMS = {"fields": "name,cca2,region,subregion,population,area,capital,continents"}
    
    async def fetch_country_data(self, origin_country: str) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            for attempt in range(3):
                try:
                    logger.info(f"Fetching data for {origin_country} (Attempt {attempt + 1})")
                    resp = await client.get(
                        self.BASE_URL.format(origin_country=origin_country),
                        params=self.PARAMS,
                        headers=self.HEADERS,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    logger.info(f"Data fetched successfully for {origin_country}")
                    return data.get('data', [])
                except HTTPStatusError as e:
                    if e.response.status_code == 429:
                        logger.warning("Rate limit exceeded, waiting for 60 seconds before retrying...")
                        await asyncio.sleep(60)
                    elif e.response.status_code in {401, 403}:
                        raise AuthenticationError("Authentication failed, check your credentials.")
                    else:
                        logger.error(f"HTTP error occurred: {e}")
                        break
                except Exception as e:
                    logger.error(f"An error occurred: {e}")
                    break
            logger.error(f"Failed to fetch data for {origin_country} after 3 attempts")
            return []

    async def extract(self, origin_countries: List[str]) -> List[Dict[str, Any]]:
        results = []
        for country in origin_countries:
            country_data = await self.fetch_country_data(country)
            results.extend(country_data)
        return results