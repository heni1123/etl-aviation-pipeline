CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.pipeline_runs (
    run_id                              TEXT NOT NULL,
    start_time                          TIMESTAMPTZ NOT NULL,
    end_time                            TIMESTAMPTZ,
    status                              TEXT NOT NULL,
    error_message                       TEXT,
    PRIMARY KEY (run_id)
);