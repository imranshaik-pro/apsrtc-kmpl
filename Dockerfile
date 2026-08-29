FROM python:3.9-slim

WORKDIR /app

# Install system dependencies (for lxml, etc.) and gdrive
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    libxml2-dev \
    libxslt-dev \
    libffi-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install gdrive
RUN wget -O /tmp/gdrive.tar.gz "https://github.com/glotlabs/gdrive/releases/download/3.9.0/gdrive_linux-x64.tar.gz" \
    && tar -xzf /tmp/gdrive.tar.gz -C /usr/local/bin/ \
    && chmod +x /usr/local/bin/gdrive \
    && rm /tmp/gdrive.tar.gz

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Default command
CMD ["python", "run_daily_report.py", "--help"]
