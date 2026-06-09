# ETL Pipeline Documentation

## Architecture Overview
This ETL pipeline is designed to extract data from various APIs, transform it according to specified business rules, and load it into the target PostgreSQL database `analytics.cible`. The pipeline consists of three main data sources:

1. **Fetch positions avions en vol**: Retrieves real-time flight data.
2. **Fetch route + compagnie par callsign**: Fetches route and airline information based on the aircraft's callsign.
3. **Fetch métadonnées pays par code ISO**: Obtains country metadata using ISO codes.

The data is processed and validated against defined business rules before being loaded into the target database.

## Setup Instructions
To set up the ETL pipeline, follow these steps:

1. **Install Required Packages**:
   Ensure you have Python 3.8 or higher installed. Then, install the required packages using pip:
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
This will initiate the extraction, transformation, and loading processes.

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

The table consists of 42 columns in total, adhering to the specified data types and constraints. 

## Business Rules Summary
The ETL process includes the following business rules:

1. **BR1**: Unique identifier for the aircraft must not be None.
2. **BR2**: Callsign must be cleaned and uppercased.
3. **BR3**: Origin country must be a valid ISO code.
4. **BR4**: Time position must be a valid Unix timestamp.
5. **BR5**: Additional business rules as defined in the specifications.

This documentation provides a comprehensive overview of the ETL pipeline, its setup, execution, and the structure of the data being processed.