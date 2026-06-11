CREATE SCHEMA IF NOT EXISTS analytics;

CREATE ROLE etl_agent WITH LOGIN PASSWORD 'your_password_here';

GRANT CONNECT ON DATABASE your_database_name TO etl_agent;

GRANT USAGE ON SCHEMA analytics TO etl_agent;