# ETL Project Documentation

## Project Overview
This ETL project is designed to extract, transform, and load data related to aircraft positions and metadata into the target database `analytics.cible`. The pipeline fetches data from multiple APIs, processes it according to defined business rules, and loads it into a PostgreSQL database.

## Architecture Overview
The architecture of the ETL pipeline consists of the following components:
- **Data Sources**: The pipeline fetches data from three primary APIs:
  1. **Fetch positions avions en vol**: Provides real-time aircraft position data.
  2. **Fetch route + compagnie par callsign**: Retrieves route and airline information based on the aircraft's callsign.
  3. **Fetch métadonnées pays par code ISO**: Supplies country metadata based on ISO codes.
- **Transformation Logic**: The data is transformed according to specified business rules before loading.
- **Target Database**: The processed data is loaded into the `analytics.cible` PostgreSQL database using a truncate and insert strategy.

## Setup Instructions
To set up the project, follow these steps:

1. **Install Required Packages**:
   Ensure you have Python installed, then run the following command to install the necessary packages:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   Create a `.env` file in the root directory of the project and add the following environment variables:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/analytics.cible
   ```

## How to Run the Pipeline
To execute the ETL pipeline, run the following command in your terminal:
```bash
python main.py
```
Ensure that your PostgreSQL database is running and accessible.

## Table Schema Summary
The target table in the `analytics.cible` database contains the following columns:

| Column Name         | Data Type |
|---------------------|-----------|
| icao24              | TEXT      |
| callsign            | TEXT      |
| origin_country      | TEXT      |
| time_position       | INTEGER   |
| last_contact        | INTEGER   |
| longitude           | FLOAT     |
| latitude            | FLOAT     |
| baro_altitude      | FLOAT     |
| on_ground           | BOOLEAN   |
| velocity            | FLOAT     |
| true_track          | FLOAT     |
| vertical_rate       | FLOAT     |
| geo_altitude        | FLOAT     |
| squawk              | TEXT      |
| spi                 | BOOLEAN   |
| callsign_iata       | TEXT      |
| airline_name        | TEXT      |
| airline_iata        | TEXT      |
| airline_icao        | TEXT      |
| dep_airport_iata    | TEXT      |
| ...                 | ...       |

The table consists of 42 columns in total, adhering to the defined schema for the ETL process.

## Business Rules Summary
The following business rules are applied during the transformation process:

1. **BR1**: Unique identifier for the aircraft (icao24).
2. **BR2**: Radio call sign of the aircraft (callsign).
3. **BR3**: Country of registration according to ICAO (origin_country).
4. **BR4**: Unix timestamp of the last known GPS position (time_position).
5. **BR5**: Indicates whether the aircraft is on the ground (on_ground). 

This documentation provides a comprehensive overview of the ETL project, including setup instructions, execution guidelines, and schema details.