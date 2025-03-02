FROM python:3.9

WORKDIR /app

# Install wait-for-it script
RUN apt-get update && apt-get install -y wait-for-it

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Command will be provided by docker-compose
CMD ["python", "./scripts/etl_pipeline.py"]