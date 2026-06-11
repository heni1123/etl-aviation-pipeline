CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.flight_operations_enriched (
    icao24 VARCHAR(10) NOT NULL,
    callsign VARCHAR(20),
    callsign_clean VARCHAR(20),
    origin_country VARCHAR(50),
    time_position BIGINT,
    last_contact BIGINT NOT NULL,
    longitude NUMERIC(10,6),
    latitude NUMERIC(10,6),
    baro_altitude NUMERIC(10,6),
    on_ground BOOLEAN NOT NULL,
    velocity NUMERIC(10,6),
    true_track NUMERIC(10,6),
    -- Add remaining columns here with their respective types and constraints
    PRIMARY KEY (icao24)
) WITH (OIDS=FALSE);

-- Load strategy: full_load

CREATE INDEX idx_callsign ON analytics.flight_operations_enriched (callsign);
CREATE INDEX idx_last_contact ON analytics.flight_operations_enriched (last_contact);