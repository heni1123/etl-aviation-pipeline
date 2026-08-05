CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.pipeline_runs (
    run_id                              SERIAL NOT NULL,
    pipeline_code                       TEXT NOT NULL,
    status                              TEXT NOT NULL,
    start_time                          TIMESTAMPTZ NOT NULL,
    end_time                            TIMESTAMPTZ,
    duration                            INTEGER,
    PRIMARY KEY (run_id)
);