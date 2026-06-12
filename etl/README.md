# ETL Project Documentation

## Project Overview
This ETL project is designed to extract, transform, and load data related to aircraft positions and metadata into the target database `analytics.cible`. The pipeline fetches data from multiple APIs, processes it according to defined business rules, and loads it into a PostgreSQL database.

## Architecture Overview
The architecture consists of the following components:
- **Data Sources**: 
  - Fetch positions of aircraft in flight from [OpenSky Network](https://opensky-network.org/api/states/all).
  - Fetch route and airline information by callsign from [ADSB Database](https://api.adsbdb.com/v0/callsign/{callsign}).
  - Fetch country metadata by ISO code from [REST Countries](https://restcountries.com/v3.1/alpha/{code}).
- **Data Processing**: The data is processed according to business rules to ensure data integrity and quality.
- **Target Database**: The processed data is loaded into the `analytics.cible` PostgreSQL database using a truncate and insert strategy.

## Setup Instructions
To set up the project, follow these steps:

1. **Install Required Packages**:
   Ensure you have Python 3.8 or higher installed. Then, install the required packages using pip:
   ```
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   Create a `.env` file in the root directory of the project and configure the following environment variables:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/analytics.cible
   ```

## How to Run the Pipeline
To run the ETL pipeline, execute the following command in your terminal:
```
python main.py
```
This will initiate the extraction of data from the specified APIs, apply the transformation rules, and load the data into the target database.

## Table Schema Summary
The target table in the `analytics.cible` database contains the following columns:

| Column Name         | Data Type | Nullable |
|---------------------|-----------|----------|
| icao24              | TEXT      | NO       |
| callsign            | TEXT      | YES      |
| origin_country      | TEXT      | YES      |
| time_position       | INTEGER   | YES      |
| last_contact        | INTEGER   | YES      |
| longitude           | FLOAT     | YES      |
| latitude            | FLOAT     | YES      |
| baro_altitude      | FLOAT     | YES      |
| on_ground           | BOOLEAN   | YES      |
| velocity            | FLOAT     | YES      |
| true_track          | FLOAT     | YES      |
| vertical_rate       | FLOAT     | YES      |
| geo_altitude        | FLOAT     | YES      |
| squawk              | TEXT      | YES      |
| spi                 | BOOLEAN   | YES      |
| callsign_iata       | TEXT      | YES      |
| airline_name        | TEXT      | YES      |
| airline_iata        | TEXT      | YES      |
| airline_icao        | TEXT      | YES      |
| dep_airport_iata    | TEXT      | YES      |
| ...                 | ...       | ...      |

This schema includes a total of 42 columns, adhering to the defined business rules and data types.