import aiohttp
import asyncio
import logging
from typing import List, Dict, Any, Optional

class AdsBDBEnrichmentExtractor:
    BASE_URL = "https://api.adsbdb.com/v0/callsign/{callsign}"

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def fetch_callsign_data(self, session: aiohttp.ClientSession, callsign: str) -> Optional[Dict[str, Any]]:
        url = self.BASE_URL.format(callsign=callsign.strip().upper())
        try:
            async with session.get(url) as response:
                if response.status == 404:
                    self.logger.warning(f"Callsign {callsign} not found.")
                    return None
                response.raise_for_status()
                data = await response.json()
                return data.get('response', {}).get('flightroute', None)
        except aiohttp.ClientError as e:
            self.logger.error(f"Error fetching data for callsign {callsign}: {e}")
            return None

    async def enrich_data(self, callsigns: List[str]) -> List[Dict[str, Any]]:
        enriched_data = []
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_callsign_data(session, callsign) for callsign in callsigns]
            results = await asyncio.gather(*tasks)

            for callsign, result in zip(callsigns, results):
                if result is not None:
                    enriched_data.append(result)
                else:
                    enriched_data.append({
                        "callsign": callsign,
                        "route": None,
                        "airline": None
                    })
        return enriched_data

    def run(self, callsigns: List[str]) -> List[Dict[str, Any]]:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.enrich_data(callsigns))