import logging
from typing import List, Dict
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.exc import SQLAlchemyError

class DataLoader:
    def __init__(self, db_url: str) -> None:
        self.db_url = db_url
        self.engine = create_engine(self.db_url)
        self.metadata = MetaData()
        logging.basicConfig(level=logging.INFO)

    async def load_data(self, transformed_list: List[Dict]) -> None:
        try:
            with self.engine.connect() as connection:
                for record in transformed_list:
                    await self._insert_record(connection, record)
                logging.info("Data loaded successfully into PostgreSQL.")
        except SQLAlchemyError as e:
            logging.error(f"Error loading data into PostgreSQL: {e}")

    async def _insert_record(self, connection, record: Dict) -> None:
        insert_query = """
        INSERT INTO flight_traffic (icao24, callsign, origin_country, destination_country, 
                                     departure, arrival, route, airline)
        VALUES (:icao24, :callsign, :origin_country, :destination_country, 
                :departure, :arrival, :route, :airline)
        """
        await connection.execute(insert_query, {
            'icao24': record['icao24'],
            'callsign': record['callsign'],
            'origin_country': record['origin_country'],
            'destination_country': record['destination_country'],
            'departure': record['departure'],
            'arrival': record['arrival'],
            'route': record['route'],
            'airline': record['airline']
        })