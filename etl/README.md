# ETL Flight Traffic Data Pipeline

## Project Overview
This ETL pipeline collects real-time flight traffic data from the OpenSky Network, enriches it with route and airline information from adsbdb, and appends geographical metadata from REST Countries. The enriched data is then loaded into a PostgreSQL database for operational analysis and performance tracking.

## Installation
To set up the ETL pipeline, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/etl-flight-traffic.git
   cd etl-flight-traffic
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the PostgreSQL database:**
   - Ensure you have PostgreSQL installed and running.
   - Create a database for the ETL pipeline:
     ```sql
     CREATE DATABASE flight_traffic;
     ```

5. **Configure environment variables:**
   Create a `.env` file in the root directory and add your database connection details:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/flight_traffic
   OPENSKY_API_URL=https://opensky-network.org/api
   ADSBDB_API_URL=https://adsbdb.com/api
   REST_COUNTRIES_API_URL=https://restcountries.com/v3.1/all
   ```

## Usage
To run the ETL pipeline, execute the following command:
```bash
python main.py
```
This will initiate the data extraction from the OpenSky Network, enrichment with adsbdb and REST Countries data, and load the final dataset into the PostgreSQL database.

## Contribution
Contributions are welcome! If you would like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Make your changes and commit them (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request. 

Please ensure your code adheres to the project's coding standards and includes appropriate tests.