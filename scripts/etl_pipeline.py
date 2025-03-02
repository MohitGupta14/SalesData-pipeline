# etl_pipeline.py
import pandas as pd
import numpy as np
from datetime import datetime
import os
import psycopg2
from sqlalchemy import create_engine, text
import logging
from minio import Minio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MinIO client setup
def get_minio_client():
    return Minio(
        "minio:9000",
        access_key="minio",
        secret_key="minio123",
        secure=False
    )

# PostgreSQL connection
def get_postgres_connection():
    return create_engine(
        'postgresql+psycopg2://postgres:postgres@postgres:5432/datawarehouse'
    )

def get_airflow_connection():
    return create_engine(
        'postgresql+psycopg2://postgres:postgres@postgres:5432/airflow'
    )


def extract_data():
    """Extract sample data (or from MinIO)"""
    logger.info("Starting data extraction")
    
    # For this example, we'll generate sample data
    # In a real scenario, you might read from MinIO or external APIs
    
    # Generate synthetic sales data
    np.random.seed(42)
    
    # Date range
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    
    # Products
    products = ['Widget A', 'Widget B', 'Widget C', 'Gadget X', 'Gadget Y']
    
    # Regions
    regions = ['North', 'South', 'East', 'West', 'Central']
    
    # Generate random data
    n_records = 1000
    
    data = {
        'transaction_id': np.arange(1, n_records + 1),
        'date': np.random.choice(dates, n_records),
        'product': np.random.choice(products, n_records),
        'region': np.random.choice(regions, n_records),
        'quantity': np.random.randint(1, 50, n_records),
        'unit_price': np.random.uniform(10, 100, n_records).round(2),
    }
    
    df = pd.DataFrame(data)
    
    # Calculate total sales
    df['total_sales'] = (df['quantity'] * df['unit_price']).round(2)
    
    logger.info(f"Extracted {len(df)} records")
    
    # Save raw data to MinIO for future reference
    save_to_minio(df, 'raw-data', f'sales_data_{datetime.now().strftime("%Y%m%d")}.csv')
    
    return df

def save_to_minio(df, bucket_name, object_name):
    """Save DataFrame to MinIO as CSV"""
    logger.info(f"Saving data to MinIO: {bucket_name}/{object_name}")
    
    # Save DataFrame to a temporary CSV file
    temp_file_path = '/tmp/temp_data.csv'
    df.to_csv(temp_file_path, index=False)
    
    # Initialize MinIO client
    client = get_minio_client()
    
    # Make bucket if it doesn't exist
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
    
    # Upload the file
    client.fput_object(
        bucket_name, object_name, temp_file_path
    )
    
    # Remove temporary file
    os.remove(temp_file_path)
    logger.info(f"Successfully saved to MinIO: {bucket_name}/{object_name}")

def transform_data(df):
    """Apply transformations to the data"""
    logger.info("Starting data transformation")
    
    # 1. Convert date to datetime if it's not already
    df['date'] = pd.to_datetime(df['date'])
    
    # 2. Extract year, month, day for easier analysis
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    
    # 3. Create a day of week feature
    df['day_of_week'] = df['date'].dt.day_name()
    
    # 4. Standardize text fields
    df['product'] = df['product'].str.strip().str.upper()
    df['region'] = df['region'].str.strip().str.upper()
    
    # 5. Add a price category
    def categorize_price(price):
        if price < 25:
            return 'Low'
        elif price < 75:
            return 'Medium'
        else:
            return 'High'
    
    df['price_category'] = df['unit_price'].apply(categorize_price)
    
    # 6. Flag for large orders (quantity > 30)
    df['large_order'] = df['quantity'] > 30
    
    logger.info("Transformation complete")
    return df

def load_data(df):
    """Load transformed data to PostgreSQL"""
    logger.info("Starting data loading")
    
    engine = get_postgres_connection()
    # Create tables if they don't exist
    create_tables(engine)
    
    # Load data to PostgreSQL
    df.to_sql('sales_fact', engine, if_exists='append', index=False)
    
    # Create summary tables
    create_summary_tables(engine, df)
    
    logger.info(f"Successfully loaded {len(df)} records to PostgreSQL")


def create_tables(engine):
    """Create tables if they don't exist"""
    try:
        with engine.begin() as conn:
            # Create sales_fact table with additional columns for transformed data
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS sales_fact (
                    id SERIAL PRIMARY KEY,
                    transaction_id INTEGER,
                    date DATE,
                    product VARCHAR(100),
                    region VARCHAR(50),
                    quantity INTEGER,
                    unit_price NUMERIC(10, 2),
                    total_sales NUMERIC(12, 2),
                    year INTEGER,
                    month INTEGER,
                    day INTEGER,
                    day_of_week VARCHAR(50),
                    price_category VARCHAR(50),
                    large_order BOOLEAN
                )
            """))
            
            # Create sales_summary table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS sales_summary (
                    id SERIAL PRIMARY KEY,
                    date DATE,
                    total_sales NUMERIC(12, 2),
                    total_quantity INTEGER,
                    avg_order_value NUMERIC(10, 2),
                    region VARCHAR(50),
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create regional_summary table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS regional_summary (
                    id SERIAL PRIMARY KEY,
                    region VARCHAR(50),
                    total_sales NUMERIC(12, 2),
                    avg_order_value NUMERIC(10, 2),
                    order_count INTEGER
                )
            """))
            
            # Create product_summary table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS product_summary (
                    id SERIAL PRIMARY KEY,
                    product VARCHAR(100),
                    total_sales NUMERIC(12, 2),
                    avg_quantity NUMERIC(10, 2),
                    order_count INTEGER
                )
            """))
            
        logger.info("Tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        raise

def create_summary_tables(engine, df):
    """Create summary tables for analytics"""
    # Regional summary
    regional_summary = df.groupby('region').agg(
        total_sales=('total_sales', 'sum'),
        avg_order_value=('total_sales', 'mean'),
        order_count=('transaction_id', 'count')
    ).reset_index()
    
    # Product summary
    product_summary = df.groupby('product').agg(
        total_sales=('total_sales', 'sum'),
        avg_quantity=('quantity', 'mean'),
        order_count=('transaction_id', 'count')
    ).reset_index()
    
    # Save summaries to PostgreSQL
    regional_summary.to_sql('regional_summary', engine, if_exists='replace', index=False)
    product_summary.to_sql('product_summary', engine, if_exists='replace', index=False)

def run_etl_pipeline():
    """Run the complete ETL pipeline"""
    try:
        logger.info("Starting ETL pipeline")
        
        # Extract
        raw_data = extract_data()
        
        # Transform
        transformed_data = transform_data(raw_data)
        
        # Load
        load_data(transformed_data)
        
        logger.info("ETL pipeline completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"ETL pipeline failed: {str(e)}")
        return False

if __name__ == "__main__":
    run_etl_pipeline()