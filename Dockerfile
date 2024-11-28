# Use an official Python 3.12 slim image
FROM python:3.12-slim

# Set the working directory
WORKDIR /gaof_weather

# Copy ATT internal certificate
COPY ATTINTERNALROOTv2.crt /usr/local/share/ca-certificates/ATTINTERNALROOTv2.crt

# Install system dependencies for SSL and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    build-essential \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, and wheel to ensure dependency compatibility
RUN pip install --no-cache-dir --upgrade pip setuptools wheel certifi

# Set environment variable for SSL certificates
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Copy the entire project, including setup.py
COPY . .

# Install the application using setup.py
RUN pip install --no-cache-dir --upgrade .

# Expose the port that FastAPI runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
