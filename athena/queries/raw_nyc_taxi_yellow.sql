CREATE EXTERNAL TABLE IF NOT EXISTS raw_nyc_taxi_yellow (
  vendorid INT,
  tpep_pickup_datetime TIMESTAMP,
  tpep_dropoff_datetime TIMESTAMP,
  passenger_count INT,
  trip_distance DOUBLE,
  pulocationid INT,
  dolocationid INT,
  fare_amount DOUBLE,
  total_amount DOUBLE,
  payment_type INT
)
STORED AS PARQUET
LOCATION 's3://nyc-tlc-data-2025/raw/nyc_taxi/yellow/';
