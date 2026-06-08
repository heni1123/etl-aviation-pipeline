import aiohttp
import asyncio
import logging
from typing import Dict, Any, Optional

class CountriesEnrichmentExtractor:
    BASE_URL = "https://restcountries.com/v3.1/alpha/{origin_country}"

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    async def fetch_country_metadata(self, origin_country: str) -> Optional[Dict[str, Any]]:
        url = self.BASE_URL.format(origin_country=origin_country)
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data[0] if data else None
                    elif response.status == 404:
                        self.logger.warning(f"Country not found for code: {origin_country}")
                        return None
                    else:
                        self.logger.error(f"Error fetching country {response.status}")
                        return None
            except Exception as e:
                self.logger.error(f"Exception occurred while fetching country {str(e)}")
                return None

    async def enrich_data(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        enriched_rows = []
        tasks = []

        for row in rows:
            origin_country = row.get('dep_country')
            if origin_country:
                tasks.append(self.fetch_country_metadata(origin_country))

        country_data_list = await asyncio.gather(*tasks)

        for row, country_data in zip(rows, country_data_list):
            if country_data:
                row['country_name'] = country_data.get('name', {}).get('common', None)
                row['region'] = country_data.get('region', None)
                row['subregion'] = country_data.get('subregion', None)
                row['population'] = country_data.get('population', None)
                row['area'] = country_data.get('area', None)
                row['capital'] = country_data.get('capital', [None])[0]
                row['continents'] = country_data.get('continents', [])
            else:
                row['country_name'] = None
                row['region'] = None
                row['subregion'] = None
                row['population'] = None
                row['area'] = None
                row['capital'] = None
                row['continents'] = []

            enriched_rows.append(row)

        return enriched_rows

    async def run(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return await self.enrich_data(rows)