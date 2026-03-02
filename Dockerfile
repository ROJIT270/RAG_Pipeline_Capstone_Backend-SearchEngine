# Use Python 3.12 (more stable for Docker than 3.14 right now)
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for building C-based libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your project files
COPY . .

# Keep the container running
CMD ["python", "query_data.py"]
