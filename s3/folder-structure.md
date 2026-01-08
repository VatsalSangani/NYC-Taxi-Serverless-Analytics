## Amazon S3 – Data Lake Storage

Amazon S3 is used as the primary storage layer for this project, acting as a simple and fully serverless data lake. All datasets and query outputs are stored in S3, while compute is handled by Athena and AWS Lambda.

### Why S3
- Fully managed and serverless
- Highly durable and cost-effective for analytical workloads
- Natively integrated with Athena and AWS Glue
- No cluster or infrastructure management required

---

### S3 Bucket Structure

```
s3://nyc-tlc-data-2025/
├─ raw/
│ └─ nyc_taxi/
│ └─ yellow/
│ └─ *.parquet
├─ curated/
│ └─ nyc_taxi/
│ └─ yellow/
│ └─ yr=2025/
│ └─ mo=01/
│ └─ *.parquet
├─ athena-results/
│ └─ query-output/

```


---

### Raw Data Layer

**Path**
s3://nyc-tlc-data-2025/raw/nyc_taxi/yellow/


**Role**
- Stores minimally processed NYC Yellow Taxi trip data
- Serves as the source for Athena external tables
- Preserves the original schema as closely as possible

**Design Decisions**
- Data stored in **Parquet** for reduced storage and scan cost
- No partitioning applied to keep ingestion simple
- Not intended for frequent analytical queries

This layer prioritizes **data fidelity and simplicity** over performance.

---

### Curated Data Layer (Partitioned)

**Path**
s3://nyc-tlc-data-2025/curated/nyc_taxi/yellow/

**Partitioning Strategy**
yr=<year>/mo=<month>


**Example**
s3://nyc-tlc-data-2025/curated/nyc_taxi/yellow/yr=2025/mo=01/


**Role**
- Stores cleaned and analytics-ready data
- Optimized for Athena queries
- Includes derived fields such as trip duration

**Why partition by year and month**
- Most queries filter by time
- Athena scans only relevant partitions
- Significantly reduces query cost and latency

Partitions are defined in the Athena CTAS statement and automatically mapped to S3 folder paths.

---

### Athena Query Results Storage

**Path**
s3://nyc-tlc-data-2025/athena-results/


**Role**
- Stores Athena query execution results
- Required for Athena to operate
- Used by Lambda when returning query responses

The Lambda execution role requires write access to this prefix.

---

### Security & Access Control

- S3 access is restricted via IAM roles
- Lambda has:
  - Read access to `raw/` and `curated/`
  - Write access to `athena-results/`
- No public access is enabled on the bucket

---

### Cost Considerations

- Parquet reduces storage and query scan size
- Partition pruning minimizes data scanned by Athena
- Raw data is not queried directly unless required
- Curated data is the primary source for analytics

This design keeps S3 costs predictable and low while supporting analytical workloads efficiently.
