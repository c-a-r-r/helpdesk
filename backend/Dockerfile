# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory for SQLite database (fallback)
RUN mkdir -p /app/data

# Create startup script
RUN echo '#!/bin/bash\necho "Starting backend application..."\necho "Waiting for database to be ready..."\nsleep 5\necho "Initializing database..."\npython init_db.py\necho "Adding sample data..."\npython add_sample_data.py\necho "Starting FastAPI server..."\nuvicorn main:app --host 0.0.0.0 --port 8000' > /app/start.sh && chmod +x /app/start.sh

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["/app/start.sh"]
