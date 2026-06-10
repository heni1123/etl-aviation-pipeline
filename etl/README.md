# ETL Pipeline Documentation

## Architecture Overview
This ETL pipeline is designed to extract data from various APIs, transform it according to specified business rules, and load it into the target PostgreSQL database `analytics.cible`. The pipeline fetches real-time flight data, route information, and country metadata to provide comprehensive insights into aviation data.

## Setup Instructions
To set up the environment for this ETL pipeline, follow these steps:

1. **Install Required Packages**
   Ensure you have Python 3.8 or higher installed. Use pip to install the necessary packages:
   ```bash
   pip install requests psycopg2-binary python-dotenv
   ```

2. **Environment Configuration**
   Create a `.env` file in the root directory of the project and add the following environment variables:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/analytics.cible
   ```

## How to Run the Pipeline
To execute the ETL pipeline, run the following command in your terminal:
```bash
python etl_pipeline.py
```
Ensure that your PostgreSQL database is running and accessible.

## Table Schema Summary
The target table in the `analytics.cible` database contains the following columns:

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
| ...                  | ...       |

## Business Rules Summary
The following business rules are applied during the transformation process:

1. **BR1**: Unique identifier for the aircraft (`icao24`) must be present.
2. **BR2**: Callsign must be stripped and uppercased.
3. **BR3**: Origin country must be available.
4. **BR4**: Timestamp of the last known GPS position (`time_position`) must be a valid integer.
5. **BR5**: Additional business rules as defined in the specifications.

This documentation provides a comprehensive overview of the ETL pipeline, including setup instructions, execution guidelines, and schema details.