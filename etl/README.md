# AVIATION-OPS-001 ETL Project

## Architecture Overview
The AVIATION-OPS-001 project is designed to extract, transform, and load aviation data into the `analytics.flight_operations_enriched` PostgreSQL database. The pipeline integrates data from multiple sources, including the OpenSky Network, ADSBDB, and REST Countries API, to provide enriched flight operation insights.

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- PostgreSQL database

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/aviation-ops-001.git
   cd aviation-ops-001
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory with the following content:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/analytics
   ```

## How to Run the Pipeline
To execute the ETL pipeline, run the following command:
```bash
python main.py
```
Ensure that your PostgreSQL database is running and accessible.

## Table Schema Summary
The `analytics.flight_operations_enriched` table consists of the following columns:

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

### Business Rules
The following business rules are applied during the transformation process:
1. **Altitude Category**: Categorizes altitude based on barometric altitude.
2. **Speed Category**: Categorizes speed based on velocity.

This project aims to provide a comprehensive view of flight operations, enabling better analysis and decision-making in aviation management.