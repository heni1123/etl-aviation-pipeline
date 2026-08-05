# AVIATION-OPS-001 ETL Project

## Architecture Overview
The AVIATION-OPS-001 project is designed to extract, transform, and load aviation data into the `analytics.flight_operations_enriched` PostgreSQL database. The pipeline integrates data from multiple sources, including the OpenSky Network, ADSBDB, and REST Countries API, to provide enriched flight operation insights.

## Setup Instructions
To set up the project, follow these steps:

1. **Install Required Packages**
   Ensure you have Python 3.8 or higher installed. Use pip to install the necessary packages:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   Create a `.env` file in the root directory of the project and add the following environment variables:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/analytics
   ```

## How to Run the Pipeline
To execute the ETL pipeline, run the following command in your terminal:
```bash
python main.py
```
This will initiate the extraction of data from the specified APIs, apply the necessary transformations, and load the data into the target PostgreSQL database.

## Table Schema Summary
The target table `analytics.flight_operations_enriched` consists of 43 columns with the following schema:

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

## Business Rules
The project implements 4 business rules to categorize data based on specific criteria, ensuring data quality and integrity.