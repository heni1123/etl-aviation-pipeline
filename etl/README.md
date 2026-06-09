# AVIATION-OPS-001 ETL Pipeline Documentation

## Architecture Overview
The AVIATION-OPS-001 ETL pipeline is designed to extract, transform, and load aviation operational data into the `analytics.flight_operations_enriched` PostgreSQL database. The pipeline integrates data from multiple sources, including the OpenSky Network, ADSBDB, and REST Countries API, to provide enriched flight operation insights.

## Setup Instructions
To set up the environment for the AVIATION-OPS-001 ETL pipeline, follow these steps:

1. **Install Required Packages**
   Ensure you have Python 3.8 or higher installed. Use pip to install the necessary packages:
   ```bash
   pip install requests psycopg2-binary python-dotenv
   ```

2. **Environment Configuration**
   Create a `.env` file in the root directory of the project and add the following environment variables:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/analytics
   ```

## How to Run the Pipeline
To execute the ETL pipeline, run the following command in your terminal:
```bash
python etl_pipeline.py
```
Ensure that the database is running and accessible as specified in the `.env` file.

## Table Schema Summary
The target table `analytics.flight_operations_enriched` contains the following columns:

| Column Name          | Data Type |
|----------------------|-----------|
| icao24               | TEXT      |
| callsign             | TEXT      |
| origin_country       | TEXT      |
| time_position        | INTEGER   |
| last_contact         | INTEGER   |
| longitude            | FLOAT     |
| latitude             | FLOAT     |
| baro_altitude       | FLOAT     |
| on_ground            | BOOLEAN   |
| velocity             | FLOAT     |
| true_track           | FLOAT     |
| vertical_rate        | FLOAT     |
| geo_altitude         | FLOAT     |
| squawk               | TEXT      |
| spi                  | BOOLEAN   |
| callsign_iata        | TEXT      |
| airline_name         | TEXT      |
| airline_iata         | TEXT      |
| airline_icao         | TEXT      |
| dep_airport_iata     | TEXT      |
| arr_airport_iata     | TEXT      |
| altitude_category     | TEXT      |
| speed_category        | TEXT      |
| ...                  | ...       |

The table consists of 43 columns in total, with various data types including TEXT, INTEGER, FLOAT, and BOOLEAN. The pipeline applies 4 business rules to categorize altitude and speed based on the provided data.