FROM python:3.9-slim

WORKDIR /app

# Install system dependencies (for lxml, pandas, etc.)
RUN apt-get update && apt-get install -y \
    gcc \
    libxml2-dev \
    libxslt-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Default command (overridden at runtime)
CMD ["python", "run_daily_report.py", "--help"]
