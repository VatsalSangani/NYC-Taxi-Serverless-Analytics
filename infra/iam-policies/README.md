## Infra: IAM Policies

This project uses AWS Lambda to run Amazon Athena queries over data stored in S3. To keep permissions tight (least privilege), the Lambda execution role needs access to:

- Athena query execution (Start/Get results)
- Glue Data Catalog (read metadata for tables)
- S3 (read dataset + write Athena query results)
- CloudWatch Logs (Lambda logging)

### 1) Lambda Execution Role (minimum required)

**Athena**
- `athena:StartQueryExecution`
- `athena:GetQueryExecution`
- `athena:GetQueryResults`
- `athena:StopQueryExecution`

**Glue Data Catalog (read-only)**
- `glue:GetDatabase`
- `glue:GetDatabases`
- `glue:GetTable`
- `glue:GetTables`
- `glue:GetPartition`
- `glue:GetPartitions`

**S3**
- Read taxi data (raw/curated prefixes)
  - `s3:GetObject`
  - `s3:ListBucket`
- Write Athena query results (the Athena output location)
  - `s3:PutObject`
  - `s3:GetBucketLocation`

**CloudWatch Logs**
- `logs:CreateLogGroup`
- `logs:CreateLogStream`
- `logs:PutLogEvents`

### 2) Required S3 Locations

You must configure two S3 locations:

- **Dataset** (read access):  
  `s3://nyc-tlc-data-2025/raw/nyc_taxi/yellow/`  
  `s3://nyc-tlc-data-2025/curated/nyc_taxi/yellow/`

- **Athena query results output** (write access):  
  Example: `s3://nyc-tlc-data-2025/athena-results/`

Athena will fail if the Lambda role cannot write to the output bucket/prefix.

### 3) Security Notes (non-negotiable)

- Do **not** use `s3:*` on `*`. Scope access to the specific bucket and prefixes.
- Do **not** use `athena:*` on `*` unless you’re prototyping. Tighten permissions for production.
- If using API Gateway, prefer **IAM auth or a custom authorizer**. Do not leave it public unless it’s intentionally a demo.
