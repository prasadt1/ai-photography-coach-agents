FROM python:3.11-slim

WORKDIR /app

# Copy only necessary files
COPY requirements.txt .
COPY agents_capstone/ ./agents_capstone/
COPY demo_3_platforms.py .
COPY demo_eval.py .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command: run demo
CMD ["python3", "demo_3_platforms.py"]
