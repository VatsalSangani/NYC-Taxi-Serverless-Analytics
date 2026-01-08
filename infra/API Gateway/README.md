## Infra: API Gateway

Amazon API Gateway (HTTP API) is used as a lightweight frontend to invoke the Lambda function that runs Athena queries and returns JSON responses.

The API is designed to expose a small number of read-only analytics endpoints over NYC Taxi data.

### 1) API Type
- **API Gateway HTTP API**
- Chosen over REST API for:
  - Lower cost
  - Simpler configuration
  - Lower latency

### 2) Integration
- **Integration type:** Lambda proxy integration
- **Target:** `api/lambda_function.py`
- **Timeout:** Configured to handle Athena query execution (Lambda polls for completion)

### 3) Routes

| Method | Path | Description |
|------|------|------------|
| GET | `/health` | Health check (no Athena call) |
| GET | `/summary/monthly` | Monthly trip and revenue summary |
| GET | `/analytics/top-pickup-zones` | Top pickup zones by trip count |

Routes are handled inside the Lambda function using request path routing.

### 4) Request Parameters
Query parameters are passed through API Gateway and forwarded directly to Lambda.

Example:
GET /summary/monthly?year=2025&month=01


### 5) Authentication & Access Control
- This project uses **open access** for demonstration purposes.
- No write operations are exposed.
- In production, recommended options include:
  - IAM authorization
  - Lambda authorizers
  - Amazon Cognito

### 6) Error Handling
- Invalid parameters return `400 Bad Request`
- Athena query failures return `500 Internal Server Error`
- Timeouts are handled by limiting query scope (partition filters)

### 7) Logging & Monitoring
- API Gateway access logs (optional)
- Lambda logs stored in CloudWatch
- Athena query execution IDs logged for debugging
