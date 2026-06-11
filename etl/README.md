# ETL Project Documentation

## Project Overview
This ETL project is designed to fetch and process real-time flight data, integrating multiple data sources to populate the target database `analytics.cible`. The pipeline extracts data from various APIs, applies business rules, and loads the data into a PostgreSQL database.

## Architecture Overview
The architecture consists of the following components:
- **Data Sources**: 
  - Fetch positions of aircraft in flight from the OpenSky Network API.
  - Fetch route and airline information by callsign from the ADSB Database API.
  - Fetch country metadata by ISO code from the REST Countries API.
- **ETL Process**: 
  - Extract data from the APIs.
  - Transform the data according to defined business rules.
  - Load the transformed data into the target PostgreSQL database.

## Setup Instructions
To set up the project, follow these steps:

1. **Install Required Packages**:
   Ensure you have Python 3.7 or higher installed. Then, install the required packages using pip:
   ```
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   Create a `.env` file in the root directory of the project and add the following environment variables:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/analytics.cible
   ```

## How to Run the Pipeline
To execute the ETL pipeline, run the following command in your terminal:
```
python main.py
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

The table contains a total of 42 columns, adhering to the specified data types and constraints. 

## Business Rules Summary
The ETL process applies the following business rules:

1. **BR1**: `icao24` - Unique identifier for the aircraft based on ICAO 24-bit code.
2. **BR2**: `callsign` - Radio call sign of the aircraft, can contain spaces.
3. **BR3**: `origin_country` - Country of registration according to ICAO database.
4. **BR4**: `time_position` - Unix timestamp of the last known GPS position.
5. **BR5**: Additional rules as defined in the project specifications.

This documentation provides a comprehensive overview of the ETL project, including architecture, setup, execution, and schema details.