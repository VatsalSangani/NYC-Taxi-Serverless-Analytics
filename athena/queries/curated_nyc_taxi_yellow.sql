CREATE TABLE curated_nyc_taxi_yellow
WITH (
  format = 'PARQUET',
  parquet_compression = 'SNAPPY',
  partitioned_by = ARRAY['yr','mo'],
  external_location = 's3://nyc-tlc-data-2025/curated/nyc_taxi/yellow/'
) AS
SELECT
  vendorid,
  passenger_count,
  trip_distance,
  pulocationid,
  dolocationid,
  fare_amount,
  total_amount,
  payment_type,
  date_diff('second', tpep_pickup_datetime, tpep_dropoff_datetime) AS trip_duration_seconds,
  year(tpep_pickup_datetime) AS yr,
  month(tpep_pickup_datetime) AS mo
FROM raw_nyc_taxi_yellow
WHERE
  tpep_pickup_datetime IS NOT NULL
  AND tpep_dropoff_datetime IS NOT NULL
  AND tpep_dropoff_datetime > tpep_pickup_datetime
  AND trip_distance > 0
  AND fare_amount > 0
  AND total_amount > 0;
