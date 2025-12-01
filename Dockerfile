# Air Drums Web Application - Dockerfile
# Multi-stage build for optimized production image

# Stage 1: Base image with system dependencies
FROM python:3.9-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV and audio processing
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Dependencies stage
FROM base as dependencies

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 3: Production image
FROM dependencies as production

# Copy application files
COPY app.py .
COPY templates/ ./templates/
COPY static/ ./static/
COPY audio/ ./audio/
COPY config.json .

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose Flask port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" || exit 1

# Run Flask application
CMD ["python", "app.py"]

# Stage 4: Development image (includes dev dependencies)
FROM dependencies as development

# Install development dependencies
RUN pip install --no-cache-dir \
    gunicorn \
    flask-debugtoolbar

# Copy application files
COPY app.py .
COPY templates/ ./templates/
COPY static/ ./static/
COPY audio/ ./audio/
COPY config.json .

# Expose Flask port
EXPOSE 5000

# Set environment variables for development
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1

# Run Flask with debug mode
CMD ["python", "app.py"]

