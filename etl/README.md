# AVIATION-OPS-001 ETL Project

## Architecture Overview
The AVIATION-OPS-001 project is designed to extract, transform, and load aviation data into the `analytics.flight_operations_enriched` PostgreSQL database. The pipeline integrates data from multiple sources, including the OpenSky Network, ADSBDB, and REST Countries API, to provide enriched flight operation insights.

## Setup Instructions
To set up the project, follow these steps:

1. **Install Required Packages**
   Ensure you have Python 3.8 or higher installed. Then, install the required packages using pip:

   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   Create a `.env` file in the root directory of the project and add the following environment variables:

   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/analytics
   ```

   Replace `username`, `password`, and other connection details with your PostgreSQL credentials.

## How to Run the Pipeline
To execute the ETL pipeline, run the following command in your terminal:

```bash
python main.py
```

This command will initiate the extraction of data from the specified APIs, apply the necessary transformations, and load the data into the target PostgreSQL database.

## Table Schema Summary
The `analytics.flight_operations_enriched` table consists of the following columns:

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

The table contains a total of 43 columns, with various data types including TEXT, INTEGER, FLOAT, and BOOLEAN. 

## Business Rules
The following business rules are applied during the transformation process:

1. **BR1**: Categorizes altitude based on barometric altitude.
2. **BR3**: Categorizes speed based on velocity.

This project aims to provide a comprehensive view of flight operations, enabling better analysis and decision-making in aviation operations.