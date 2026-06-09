import os
import psycopg2
import psycopg2.extras
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Loader:
    def load(self, rows: List[Dict[str, Any]]) -> None:
        try:
            conn = psycopg2.connect(
                host=os.environ["DB_HOST"],
                port=os.environ.get("DB_PORT", "5432"),
                dbname=os.environ["DB_NAME"],
                user=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"],
            )
            conn.autocommit = False
            
            with conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE analytics.cible")
                psycopg2.extras.execute_batch(
                    cur,
                    "INSERT INTO analytics.cible (icao24, callsign, origin_country, time_position) VALUES %s",
                    [(row['icao24'], row['callsign'].strip().upper(), row['origin_country'], row['time_position']) for row in rows],
                    page_size=100,
                )
            conn.commit()
            logger.info(f"Rows loaded: {len(rows)}")
            self.audit_load(len(rows))
        except Exception as e:
            logger.error(f"Error during loading: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def audit_load(self, rows_loaded: int) -> None:
        try:
            conn = psycopg2.connect(
                host=os.environ["DB_HOST"],
                port=os.environ.get("DB_PORT", "5432"),
                dbname=os.environ["DB_NAME"],
                user=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"],
            )
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO analytics.pipeline_runs (rows_loaded) VALUES (%s)",
                    (rows_loaded,)
                )
            conn.commit()
        except Exception as e:
            logger.error(f"Error during audit logging: {e}")
            conn.rollback()
        finally:
            conn.close()