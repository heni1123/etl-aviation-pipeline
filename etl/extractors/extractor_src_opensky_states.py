import httpx
import asyncio
import logging
from typing import List, Dict

class AuthenticationError(Exception):
    pass

class SrcOpenskyStatesExtractor:
    def __init__(self) -> None:
        self.url = "https://opensky-network.org/api/states/all"
        self.params = {
            "lamin": "28.0",
            "lomin": "-10.0",
            "lamax": "47.0",
            "lomax": "37.0"
        }
        logging.basicConfig(level=logging.INFO)

    async def fetch_data(self) -> List[Dict]:
        retries = 3
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        self.url,
                        params=self.params,
                        headers={"Accept": "application/json"},
                    )
                    response.raise_for_status()
                    data = response.json()
                    logging.info(f"Request successful: {response.elapsed.total_seconds()} seconds")
                    return data['states']
            except httpx.HTTPStatusError as e:
                if e.response.status_code in {401, 403}:
                    raise AuthenticationError("Authentication failed") from e
                elif e.response.status_code == 429:
                    logging.warning("Rate limit exceeded, waiting 60 seconds before retrying...")
                    await asyncio.sleep(60)
                else:
                    logging.error(f"HTTP error occurred: {e}")
                    raise
            except Exception as e:
                logging.error(f"An error occurred: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
        return []  # Return an empty list if all retries fail