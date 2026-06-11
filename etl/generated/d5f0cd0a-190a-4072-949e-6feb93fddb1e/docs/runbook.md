# Operational Runbook

## Deployment

### Prerequisites
- Ensure the following environment variables are set:
  - `GITHUB_TOKEN`: GitHub Personal Access Token
  - `DB_PASSWORD`: Database Password

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/dataxiagen/etl-aviation-pipeline.git
   cd etl-aviation-pipeline
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the ETL pipeline:
   ```bash
   python main.py
   ```

## Monitoring

### Tools
- Use monitoring tools like Prometheus and Grafana to track ETL performance metrics.

### Key Metrics
- ETL execution time
- Number of records processed
- Error rates

## Alerting

### Setup Alerts
- Configure alerts for the following conditions:
  - ETL execution time exceeds threshold (e.g., 5 minutes)
  - Error rate exceeds 5%

### Notification Channels
- Use Slack or email for alert notifications.

## Rollback

### Rollback Procedure
1. Identify the last successful ETL run.
2. Restore the target database to the state of the last successful run using:
   ```sql
   DELETE FROM public.target_data;
   INSERT INTO public.target_data SELECT * FROM public.target_data_backup WHERE run_id = 'last_successful_run_id';
   ```

3. Verify data integrity and consistency post-rollback.

## Documentation

### ETL Process
- Document the ETL process, including data sources, transformations, and business rules.

### Operational Guides
- Create operational guides for monitoring and troubleshooting the ETL pipeline.

### API Responses
- Include examples of API responses and expected data formats in documentation.

### Glossary
- Provide a glossary of terms and acronyms used in the project.