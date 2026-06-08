import aiohttp
import asyncio
import logging
from typing import List, Dict, Any

class OpenSkyExtractor:
    BASE_URL: str = "https://opensky-network.org/api/states/all"
    HEADERS: Dict[str, str] = {}

    def __init__(self) -> None:
        self.logger = self.setup_logger()

    def setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("OpenSkyExtractor")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    async def fetch_data(self) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.BASE_URL, headers=self.HEADERS, params={
                    "lamin": "28.0",
                    "lomin": "-10.0",
                    "lamax": "47.0",
                    "lomax": "37.0"
                }) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data.get("states", [])
            except aiohttp.ClientError as e:
                self.logger.error(f"HTTP error occurred: {e}")
                return []
            except Exception as e:
                self.logger.error(f"An error occurred: {e}")
                return []

    async def extract(self) -> List[Dict[str, Any]]:
        self.logger.info("Starting extraction from OpenSky API")
        data = await self.fetch_data()
        self.logger.info(f"Extracted {len(data)} records from OpenSky API")
        return data

if __name__ == "__main__":
    extractor = OpenSkyExtractor()
    asyncio.run(extractor.extract())