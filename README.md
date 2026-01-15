# NYC Taxi 2025 – Serverless Analytics (S3, Glue, Athena)

This project implements a **serverless data analytics pipeline** on AWS using NYC Yellow Taxi trip data (2025).  
It focuses on **data lake design, schema discovery, partitioned analytics, and query performance**, not over-engineered ETL.

The stack uses **Amazon S3, AWS Glue (crawler/catalog only), Amazon Athena, and AWS Lambda**, with optional API Gateway exposure.

---

## Architecture Overview

High-level flow:

```
S3 (Raw Taxi Data)
↓
AWS Glue Crawler (Schema Discovery)
↓
Glue Data Catalog
↓
Amazon Athena (SQL + CTAS)
↓
AWS Lambda (Query Execution)
↓
API Gateway (optional)

```

Architecture diagrams are available in:
```
architecture/
├─ diagram.png
└─ diagram.drawio

```


---

## Tech Stack

- **Amazon S3** – Data lake storage
- **AWS Glue** – Crawlers & Data Catalog (no ETL jobs)
- **Amazon Athena** – Serverless SQL analytics
- **AWS Lambda** – Executes Athena queries programmatically
- **API Gateway** – Optional HTTP interface
- **Parquet** – Columnar storage for performance & cost control

---

## Repository Structure
```
NYC-TAXI-2025-S3-GLUE-ATHENA/
├─ architecture/
│ ├─ diagram.png
│ └─ diagram.drawio
├─ athena/
│ ├─ ddl/
│ │ └─ create_external_table.sql
│ └─ queries/
│ ├─ raw_nyc_taxi_yellow.sql
│ └─ curated_nyc_taxi_yellow.sql
├─ data/
│ └─ yellow_tripdata_2025-*.parquet
├─ dashboard/
│ ├─ app.py
│ ├─ data.py
│ ├─ logic.py
│ ├─ charts/
│ │ ├─ kpi.py
│ │ ├─ trend.py
│ │ ├─ topn.py
│ │ └─ detail.py
│ ├─ .streamlit/
│ │ └─ config.toml
│ └─ requirements.txt
├─ Glue/
│ └─ Glue UI.png
├─ infra/
│ ├─ API Gateway/
│ │ └─ README.md
│ └─ iam-policies/
│ └─ README.md
├─ lambda/
│ └─ lambda_function.py
├─ s3/
│ └─ folder-structure.md
├─ .gitignore
├─ README.md

```


---

## S3 Data Lake Design

S3 acts as the **single storage layer** for both raw and curated data.

### Raw Data
- Stored as Parquet files
- Minimal transformation
- Used as the source for Athena external tables

Example:
```
s3://nyc-tlc-data-2025/raw/nyc_taxi/yellow/
```

Local samples are included in:
```
data/
└─ yellow_tripdata_2025-06.parquet
└─ yellow_tripdata_2025-07.parquet
...
```

---

### Curated Data (Partitioned)

Curated data is generated using **Athena CTAS** and stored in a partitioned layout:

```
yr=<year>/mo=<month>/
```

Example:
```
s3://nyc-tlc-data-2025/curated/nyc_taxi/yellow/yr=2025/mo=06/
```

**Why partitioning**
- Most queries are time-based
- Athena scans only relevant partitions
- Lower query cost and faster execution

---

## AWS Glue (Catalog Only)

Glue is used **only for schema discovery**.

### What Glue does
- Crawls raw and curated S3 paths
- Infers schemas
- Registers tables in the Glue Data Catalog

### What Glue does NOT do
- No Glue ETL jobs
- No Spark transformations
- No Glue workflows


This design avoids unnecessary compute and keeps the pipeline lightweight.

---

## Athena Layer

### DDL
Located in:
```
athena/ddl/create_external_table.sql
```
Creates an **external table** over raw S3 Parquet data.

### Queries
Located in:
```
athena/queries/
├─ raw_nyc_taxi_yellow.sql
└─ curated_nyc_taxi_yellow.sql
```


- `raw_nyc_taxi_yellow.sql`  
  Defines the raw external table

- `curated_nyc_taxi_yellow.sql`  
  Uses **CTAS** to:
  - Clean invalid records
  - Add derived columns
  - Partition by year and month

Validation logic is embedded in the CTAS `WHERE` clause.

---

## Lambda Layer

Located in:
```
lambda/lambda_function.py
```


Responsibilities:
- Accepts request parameters (year, month, query type)
- Executes Athena queries programmatically
- Polls for query completion
- Returns structured JSON responses

Lambda **does not perform heavy ETL** and is intentionally limited to orchestration and query execution.

---

## Infrastructure Notes

### IAM
Documented in:
infra/iam-policies/README.md


Lambda role includes:
- Athena query execution permissions
- Glue Data Catalog read access
- S3 read (raw/curated) and write (Athena results)
- CloudWatch logging

### API Gateway
Documented in:
infra/API Gateway/README.md


- HTTP API
- Lambda proxy integration
- Read-only analytics endpoints

---

## Cost & Performance Considerations

- Parquet minimizes data scanned
- Partition pruning reduces Athena cost
- Serverless components scale to zero
- No always-on infrastructure

The design intentionally avoids Glue ETL and Spark clusters.

---

## Known Limitations

- Not designed for real-time ingestion
- Lambda is not suitable for large-scale transformations
- Glue is used only for cataloging, not processing

These trade-offs are intentional and documented.

---

## Streamlit Data Quality Dashboard (Local)

The project includes a **local Streamlit dashboard** focused on **data quality validation** for NYC Taxi datasets processed via Athena.

The dashboard is intentionally **not deployed** and is designed to support:
- Data validation during development
- Sanity checks on raw and curated datasets
- Inspection of query outputs before downstream consumption

### Data Quality Checks
The dashboard surfaces:
- Null rate analysis per column
- Duplicate record detection
- Row count comparisons (raw vs curated)
- Basic schema-level consistency checks

These checks are **read-only** and do not modify source or curated data.

### Data Source
The dashboard consumes:
- Athena query results via AWS SDK (requires valid AWS credentials), or
- Locally available query outputs for development/testing

It does **not** perform ingestion, transformation, or orchestration.

Most checks are computed via SQL in Athena to leverage partition pruning and avoid large data transfers to the application layer.

### Run Locally
```bash
pip install -r dashboard/requirements.txt
streamlit run dashboard/app.py

```


## Future Improvements

- Terraform/CDK for full IaC
- Result caching (S3 or DynamoDB)
- Authentication (IAM / Cognito)
- Automated partition refresh

---

## License

MIT
