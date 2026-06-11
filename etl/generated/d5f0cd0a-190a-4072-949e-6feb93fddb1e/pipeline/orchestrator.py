import asyncio
import logging
import time
from typing import List, Dict, Any, Tuple
import aiohttp
import os
import psycopg2
from psycopg2 import sql

class PipelineOrchestrator:
    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run
        self.metrics = {
            'extracted': 0,
            'loaded': 0,
            'duration': 0,
            'errors': []
        }
        logging.basicConfig(level=logging.INFO)

    async def run(self) -> None:
        start_ts = time.time()
        try:
            records = await self._extract_phase()
            transformed_records = await self._transform_phase(records)
            await self._validate_phase(transformed_records)
            if not self.dry_run:
                await self._load_phase(transformed_records)
                status = 'success'
            else:
                status = 'dry_run'
        except Exception as e:
            logging.error(f"Pipeline failed: {e}")
            status = 'failed'
            self.metrics['errors'].append(str(e))
        finally:
            end_ts = time.time()
            self._audit_pipeline_run(start_ts, end_ts, status)

    async def _extract_phase(self) -> List[Dict[str, Any]]:
        url = "https://restcountries.com/v3.1/all"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch {response.status}")
                data = await response.json()
                self.metrics['extracted'] = len(data)
                return data

    async def _transform_phase(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        transformed = []
        for record in records:
            transformed_record = {
                'name': record.get('name', {}).get('common', None),
                'alpha2Code': record.get('cca2', None),
                'alpha3Code': record.get('cca3', None),
                'population': record.get('population', None),
                'area': record.get('area', None),
                'region': record.get('region', None),
                'subregion': record.get('subregion', None)
            }
            transformed.append(transformed_record)
        return transformed

    async def _validate_phase(self, records: List[Dict[str, Any]]) -> None:
        for record in records:
            if not record.get('name') or not record.get('alpha2Code'):
                raise ValueError("Validation failed: Missing required fields")

    async def _load_phase(self, records: List[Dict[str, Any]]) -> None:
        conn = None
        try:
            conn = psycopg2.connect(
                dbname='your_db_name',
                user='your_db_user',
                password=os.getenv('DB_PASSWORD'),
                host='your_db_host',
                port='your_db_port'
            )
            with conn.cursor() as cursor:
                insert_query = sql.SQL("""
                    INSERT INTO public.target_data (name, alpha2Code, alpha3Code, population, area, region, subregion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """)
                for record in records:
                    cursor.execute(insert_query, (
                        record['name'],
                        record['alpha2Code'],
                        record['alpha3Code'],
                        record['population'],
                        record['area'],
                        record['region'],
                        record['subregion']
                    ))
                conn.commit()
                self.metrics['loaded'] = len(records)
        except Exception as e:
            logging.error(f"Loading failed: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def _audit_pipeline_run(self, start_ts: float, end_ts: float, status: str) -> None:
        logging.info(f"Pipeline run completed: {status}, "
                     f"Rows extracted: {self.metrics['extracted']}, "
                     f"Rows loaded: {self.metrics['loaded']}, "
                     f"Duration: {end_ts - start_ts} seconds")