# ETL Pipeline Documentation

## Architecture Overview
This ETL pipeline is designed to fetch real-time aircraft position data, route information, and country metadata. The data is sourced from three APIs and is loaded into a PostgreSQL database named `analytics.cible`. The pipeline follows a `truncate_insert` load strategy to ensure that the target table is refreshed with the latest data.

## Setup Instructions
To set up the environment for this ETL pipeline, follow these steps:

1. **Install Required Packages**
   Ensure you have Python 3.7 or higher installed. Then, install the required packages using pip:

   ```bash
   pip install requests psycopg2-binary python-dotenv
   ```

2. **Environment Configuration**
   Create a `.env` file in the root directory of the project and add the following environment variables:

   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/analytics.cible
   ```

   Replace `username` and `password` with your PostgreSQL credentials.

## How to Run the Pipeline
To execute the ETL pipeline, run the following command in your terminal:

```bash
python etl_pipeline.py
```

Ensure that your PostgreSQL server is running and accessible.

## Table Schema Summary
The target table in the `analytics.cible` database will have the following columns:

- `icao24`: Unique identifier for the aircraft based on ICAO 24-bit code.
- `callsign`: Callsign of the aircraft, cleaned and converted to uppercase.
- `origin_country`: Country of registration according to ICAO.
- `time_position`: Unix timestamp of the last known GPS position.

## Business Rules
The following business rules are applied during the ETL process:

1. **BR1**: Unique identifier for the aircraft based on ICAO 24-bit code. (Derived from `row['icao24']`)
2. **BR2**: Callsign of the aircraft, cleaned and converted to uppercase. (Derived from `row['callsign'].strip().upper()`)
3. **BR3**: Country of registration according to ICAO. (Derived from `row['origin_country']`)
4. **BR4**: Unix timestamp of the last known GPS position. (Derived from `row['time_position']`)
5. **BR5**: Additional business rule description. (Derived from `row['additional_field']`)

This documentation provides a comprehensive overview of the ETL pipeline, including setup instructions, execution guidelines, and the schema of the target database.