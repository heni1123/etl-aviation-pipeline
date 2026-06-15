# ETL Project Documentation

## Project Overview
This ETL project is designed to fetch and process real-time flight data, integrating multiple data sources to populate the target database `analytics.cible`. The pipeline extracts data from various APIs, applies business rules, and loads the cleaned data into a PostgreSQL database.

## Architecture Overview
The architecture consists of the following components:
- **Data Sources**: 
  - Fetch positions of aircraft in flight from the OpenSky Network API.
  - Fetch route and airline information by callsign from the ADSB DB API.
  - Fetch country metadata by ISO code from the Rest Countries API.
- **ETL Process**: 
  - Extract data from the APIs.
  - Transform the data by applying business rules.
  - Load the transformed data into the PostgreSQL database `analytics.cible` using a truncate and insert strategy.

## Setup Instructions
To set up the project, follow these steps:

1. **Install Required Packages**:
   Ensure you have Python 3.7 or higher installed. Then, install the required packages using pip:
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
This will initiate the extraction, transformation, and loading process.

## Table Schema Summary
The target table in the `analytics.cible` database consists of the following columns:

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

## Business Rules Summary
The following business rules are applied during the transformation process:

1. **BR1**: Unique identifier for the aircraft must be present.
2. **BR2**: Callsign must be cleaned and uppercased.
3. **BR3**: Origin country must be a valid ISO country code.
4. **BR4**: Aircraft must not be marked as on ground for flight tracking.
5. **BR5**: Additional business rules as required.

## Data Sources
- **Fetch positions avions en vol**: [OpenSky Network API](https://opensky-network.org/api/states/all) - Status: success
- **Fetch route + compagnie par callsign**: [ADSB DB API](https://api.adsbdb.com/v0/callsign/{callsign}) - Status: success
- **Fetch métadonnées pays par code ISO**: [Rest Countries API](https://restcountries.com/v3.1/alpha/{code}) - Status: success

This documentation provides a comprehensive overview of the ETL project, including setup instructions, execution guidelines, and schema details.