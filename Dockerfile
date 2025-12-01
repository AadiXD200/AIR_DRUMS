# Air Drums Web Application - Dockerfile
# Multi-stage build for optimized production image

# Stage 1: Base image
FROM python:3.9-slim as base

# Set working directory
WORKDIR /app

# No system dependencies needed - web app only uses Flask

# Stage 2: Dependencies stage
FROM base as dependencies

# Copy requirements file (web app only needs Flask - no simpleaudio!)
# The web app uses Web Audio API in JavaScript, not Python audio libraries
COPY requirements-web.txt .

# Install Python dependencies (only Flask needed for web app)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-web.txt

# Stage 3: Production image
FROM dependencies as production

# Copy application files
COPY app.py .
COPY templates/ ./templates/
COPY static/ ./static/
COPY audio/ ./audio/
COPY config.json .
COPY start.sh .

# Make startup script executable
RUN chmod +x start.sh

# Expose port (Cloud Run will override with PORT env var, but we expose a default)
EXPOSE 8080

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
# PORT will be set by Cloud Run (defaults to 8080)

# Run with startup script (uses PORT from environment)
CMD ./start.sh

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

# Expose port
EXPOSE 8080

# Set environment variables for development
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Run Flask with debug mode
CMD ["python", "app.py"]
