FROM python:3.9-slim

WORKDIR /app

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY agent.py config.py models.py fetchers.py formatter.py delivery.py ./

# Create logs directory
RUN mkdir -p logs

# Copy .env file (mount as volume in production)
COPY .env .

# Set entrypoint
ENTRYPOINT ["python3", "agent.py"]
CMD []

# Usage:
# docker build -t apple-news-agent .
# docker run --env-file .env apple-news-agent --once
# docker run --env-file .env -d apple-news-agent (background)
