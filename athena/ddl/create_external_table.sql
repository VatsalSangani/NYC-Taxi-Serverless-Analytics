-- =====================================================
-- NYC Taxi 2025 – External Table (Processed Zone)
-- Engine: Amazon Athena
-- Format: Parquet (columnar, compressed)
-- Partitioning: year, month
-- =====================================================

CREATE EXTERNAL TABLE IF NOT EXISTS nyc_taxi_processed (
    vendor_id              STRING,
    pickup_datetime         TIMESTAMP,
    dropoff_datetime        TIMESTAMP,

    passenger_count         INT,
    trip_distance           DOUBLE,

    pickup_location_id      INT,
    dropoff_location_id     INT,

    rate_code_id            INT,
    store_and_fwd_flag      STRING,

    payment_type            INT,

    fare_amount             DOUBLE,
    extra                   DOUBLE,
    mta_tax                 DOUBLE,
    tip_amount              DOUBLE,
    tolls_amount            DOUBLE,
    improvement_surcharge   DOUBLE,
    congestion_surcharge    DOUBLE,
    airport_fee             DOUBLE,
    total_amount            DOUBLE
)
PARTITIONED BY (
    year STRING,
    month STRING
)
STORED AS PARQUET
LOCATION 's3://<YOUR-BUCKET-NAME>/nyc-taxi/processed/'
TBLPROPERTIES (
    'parquet.compress' = 'SNAPPY'
);
