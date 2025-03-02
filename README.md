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

or 

1. Clone the repo
```bash
git clone https://github.com/MohitGupta14/SalesData-pipeline
```
2. Open DockerHub and add path of your root folder to Settings<Resources<File Sharing 

3. Start the containers:

```bash
docker compose up -d
```

## Accessing the Services

- **Airflow**: http://localhost:8081 (username: mohit, password: mohit@123)
- **MinIO Console**: http://localhost:9001 (username: minio, password: minio123)
- **Adminer**: http://localhost:8080 (System: PostgreSQL, Server: postgres, Username: postgres, Password: postgres, Database: datawarehouse)

## Understanding the Pipeline

This pipeline demonstrates a complete ETL (Extract, Transform, Load) process:

1. **Extract**: 
   - Generates sample sales data
   - Stores raw data in MinIO (S3-compatible storage)
   - MinIO is a data lake, similar to AWS S3. After running the ETL container (check the YAML file), we can view our data in the MinIO UI. 
   - <img width="1470" alt="Screenshot 2025-03-02 at 2 47 57 PM" src="https://github.com/user-attachments/assets/5ba1ce4a-923e-4c83-a717-5e2d406a549b" />


2. **Transform**:
   - Adds date features (year, month, day, day of week)
   - Standardizes text fields
   - Categorizes prices
   - Flags large orders

3. **Load**:
   - Stores processed data in PostgreSQL
   - Creates summary tables for analytics
   - We can visualize the PostgreSQL table in Adminer's UI on port 8080
   - <img width="1390" alt="Screenshot 2025-03-02 at 2 53 26 PM" src="https://github.com/user-attachments/assets/ff43b0c9-c48c-4cc8-b1d9-57ba373ec20a" />


4. **Orchestration**:
   - Airflow schedules and monitors the pipeline
   - Provides a visual interface to track job execution
   - We can visualise our pipeline on port 8081
   - <img width="1452" alt="Screenshot 2025-03-02 at 4 44 21 PM" src="https://github.com/user-attachments/assets/b59f8c97-99ef-4619-9f0f-3c3cab9048ed" />


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
