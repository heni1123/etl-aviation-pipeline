# README.md

## Overview
The Unknown ETL project is designed to extract, transform, and load data from the REST Countries API into a PostgreSQL database. This project aims to provide a streamlined process for managing country data, although currently, there are no specific data sources or transformations defined.

## Architecture
The architecture of the Unknown ETL project consists of a single data extraction process from the REST Countries API. The data is fetched using a GET request and is intended to be loaded into the `public.target_data` table in a PostgreSQL database. The project is designed to be run on-demand, allowing for flexibility in data retrieval.

## Data Sources
- REST API: REST Countries
  - URL: https://restcountries.com/v3.1/all
  - Method: GET
  - Auth: none

## Target Tables
- public.target_data

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/dataxiagen/etl-aviation-pipeline.git
   ```
2. Navigate to the project directory:
   ```
   cd etl-aviation-pipeline
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration
1. Set up environment variables:
   - `GITHUB_TOKEN`: Your GitHub Personal Access Token.
   - `DB_PASSWORD`: Your PostgreSQL database password.

## Running
To execute the ETL process, run the following command:
```
python main.py
```
This will trigger the extraction of data from the REST Countries API and load it into the target table.

## Testing
To run the tests for the ETL process, use the following command:
```
pytest tests/
```
Ensure that all tests pass before deploying the ETL process to production.

## Troubleshooting
- If you encounter issues with the API request, check the URL and ensure that the API is accessible.
- Verify that the environment variables are correctly set and that the database is reachable.
- Review the logs for any error messages that may indicate the source of the problem.