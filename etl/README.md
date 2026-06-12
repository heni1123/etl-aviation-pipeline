# AVIATION-OPS-001 ETL Project

## Architecture Overview
The AVIATION-OPS-001 project is designed to extract, transform, and load aviation data into the `analytics.flight_operations_enriched` PostgreSQL database. The pipeline integrates data from multiple sources, including the OpenSky Network, ADSBDB, and REST Countries API, to provide enriched flight operation insights.

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- PostgreSQL database

### Installation
1. Clone the repository:
   ```
   git clone https://github.com/your-repo/aviation-ops-001.git
   cd aviation-ops-001
   ```

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   Create a `.env` file in the root directory with the following content:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/analytics
   ```

## How to Run the Pipeline
To execute the ETL pipeline, run the following command in your terminal:
```
python main.py
```
Ensure that your PostgreSQL database is running and accessible.

## Table Schema Summary
The target table `analytics.flight_operations_enriched` contains the following columns:

| Column Name          | Data Type | Nullable |
|----------------------|-----------|----------|
| icao24               | TEXT      | NO       |
| callsign             | TEXT      | YES      |
| origin_country       | TEXT      | YES      |
| time_position        | INTEGER   | YES      |
| last_contact         | INTEGER   | YES      |
| longitude            | FLOAT     | YES      |
| latitude             | FLOAT     | YES      |
| baro_altitude       | FLOAT     | YES      |
| on_ground            | BOOLEAN   | YES      |
| velocity             | FLOAT     | YES      |
| true_track           | FLOAT     | YES      |
| vertical_rate        | FLOAT     | YES      |
| geo_altitude         | FLOAT     | YES      |
| squawk               | TEXT      | YES      |
| spi                  | BOOLEAN   | YES      |
| callsign_iata        | TEXT      | YES      |
| airline_name         | TEXT      | YES      |
| airline_iata         | TEXT      | YES      |
| airline_icao         | TEXT      | YES      |
| dep_airport_iata     | TEXT      | YES      |
| ...                  | ...       | ...      |

## Data Sources
The pipeline integrates data from the following sources:

1. **OpenSky Network**
   - **URL**: [OpenSky API](https://opensky-network.org/api/states/all)
   - **Status**: Success

2. **ADSBDB**
   - **URL**: [ADSBDB API](https://api.adsbdb.com/v0/callsign/{callsign})
   - **Status**: Success

3. **REST Countries**
   - **URL**: [REST Countries API](https://restcountries.com/v3.1/alpha/{origin_country})
   - **Status**: Success

## Business Rules
The following business rules are applied during the transformation process:

1. **BR1**: Categorizes altitude based on barometric altitude.
2. **BR3**: Categorizes speed based on velocity.

This documentation provides a comprehensive overview of the AVIATION-OPS-001 ETL project, including setup instructions, execution guidelines, and schema details.