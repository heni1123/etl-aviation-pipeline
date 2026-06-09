import httpx
import asyncio
import logging
from typing import List, Dict

class AuthenticationError(Exception):
    pass

class SrcRestCountriesExtractor:
    def __init__(self) -> None:
        self.url_template = "https://restcountries.com/v3.1/alpha/{origin_country}"
        self.params = {
            "fields": "name,cca2,region,subregion,population,area,capital,continents"
        }
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    async def fetch_country_data(self, origin_country: str) -> Dict:
        async with httpx.AsyncClient() as client:
            for attempt in range(3):
                try:
                    self.logger.info(f"Fetching data for {origin_country}")
                    resp = await client.get(
                        self.url_template.format(origin_country=origin_country),
                        params=self.params,
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

    async def extract(self, origin_countries: List[str]) -> List[Dict]:
        results = []
        for country in origin_countries:
            country_data = await self.fetch_country_data(country)
            if country_data:
                results.append(country_data)
        return results