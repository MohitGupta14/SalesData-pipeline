# Data Engineering Pipeline with Docker

This project demonstrates a simple data engineering pipeline using Docker containers. It includes data extraction, transformation, loading, and scheduling with various tools.

## Components

- **PostgreSQL**: Database to store processed data
- **MinIO**: Object storage (S3 compatible) for raw data
- **Airflow**: Workflow orchestration and scheduling
- **PySpark/Jupyter**: Data processing environment
- **Adminer**: Database management UI

## Prerequisites

- Docker and Docker Compose
- Git (optional)

## Setup Instructions

1. Create a project directory and set up the following folder structure:

```
data-engineering-pipeline/
├── docker-compose.yml
├── dags/
│   └── sales_etl_dag.py
├── scripts/
│   └── etl_pipeline.py
├── notebooks/
├── data/
└── README.md
```

2. Copy the provided files into their respective directories.

3. Start the containers:

```bash
docker-compose up -d
```

4. Initialize Airflow (first time only):

```bash
docker exec -it airflow-webserver airflow db init
docker exec -it airflow-webserver airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
```

## Accessing the Services

- **Airflow**: http://localhost:8081 (username: admin, password: admin)
- **MinIO Console**: http://localhost:9001 (username: minio, password: minio123)
- **Adminer**: http://localhost:8080 (System: PostgreSQL, Server: postgres, Username: postgres, Password: postgres, Database: datawarehouse)
- **Jupyter Notebook**: http://localhost:8888 (Token is displayed in the container logs)

## Understanding the Pipeline

This pipeline demonstrates a complete ETL (Extract, Transform, Load) process:

1. **Extract**: 
   - Generates sample sales data
   - Stores raw data in MinIO (S3-compatible storage)

2. **Transform**:
   - Adds date features (year, month, day, day of week)
   - Standardizes text fields
   - Categorizes prices
   - Flags large orders

3. **Load**:
   - Stores processed data in PostgreSQL
   - Creates summary tables for analytics

4. **Orchestration**:
   - Airflow schedules and monitors the pipeline
   - Provides a visual interface to track job execution

## Customizing the Pipeline

To adapt this pipeline for your specific needs:

1. Modify the `etl_pipeline.py` script to use your own data source
2. Adjust transformations based on your data requirements
3. Update the database schema in the `create_tables` function
4. Change the Airflow schedule in the DAG file

## Learning Resources

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [MinIO Documentation](https://docs.min.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

## Troubleshooting

- If containers fail to start, check Docker logs: `docker-compose logs <service-name>`
- For database connection issues, ensure PostgreSQL is healthy: `docker-compose ps`
- For file permission problems, check volume mappings in `docker-compose.yml`
