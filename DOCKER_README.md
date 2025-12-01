# Docker Setup for Air Drums

This guide explains how to build and run the Air Drums web application using Docker.

## Prerequisites

- Docker Engine 20.10 or higher
- Docker Compose 1.29 or higher (optional, for docker-compose)

## Quick Start

### Using Docker Compose (Recommended)

#### Production Build:
```bash
docker-compose up --build
```

#### Development Build (with hot reload):
```bash
docker-compose -f docker-compose.dev.yml up --build
```

### Using Docker Directly

#### Build the Image:
```bash
# Production build
docker build --target production -t air-drums:latest .

# Development build
docker build --target development -t air-drums:dev .
```

#### Run the Container:
```bash
# Production
docker run -d -p 5000:5000 --name air-drums air-drums:latest

# Development
docker run -d -p 5000:5000 --name air-drums-dev air-drums:dev
```

## Access the Application

Once the container is running, open your browser and navigate to:
- **http://localhost:5000**

## Docker Compose Commands

### Start Services:
```bash
docker-compose up
```

### Start in Background (Detached Mode):
```bash
docker-compose up -d
```

### Stop Services:
```bash
docker-compose down
```

### View Logs:
```bash
docker-compose logs -f
```

### Rebuild After Changes:
```bash
docker-compose up --build
```

### Remove Everything (including volumes):
```bash
docker-compose down -v
```

## Docker Commands

### View Running Containers:
```bash
docker ps
```

### View All Containers:
```bash
docker ps -a
```

### View Logs:
```bash
docker logs air-drums
docker logs -f air-drums  # Follow logs
```

### Stop Container:
```bash
docker stop air-drums
```

### Start Container:
```bash
docker start air-drums
```

### Remove Container:
```bash
docker rm air-drums
```

### Execute Commands in Container:
```bash
docker exec -it air-drums bash
```

### Remove Image:
```bash
docker rmi air-drums:latest
```

## Environment Variables

You can customize the application using environment variables:

```bash
docker run -d -p 5000:5000 \
  -e FLASK_ENV=production \
  -e FLASK_APP=app.py \
  --name air-drums \
  air-drums:latest
```

## Volume Mounts

### For Development (Hot Reload):
```bash
docker run -d -p 5000:5000 \
  -v $(pwd)/app.py:/app/app.py \
  -v $(pwd)/templates:/app/templates \
  -v $(pwd)/static:/app/static \
  --name air-drums-dev \
  air-drums:dev
```

### For Audio Files (Read-Only):
```bash
docker run -d -p 5000:5000 \
  -v $(pwd)/audio:/app/audio:ro \
  --name air-drums \
  air-drums:latest
```

## Multi-Stage Build

The Dockerfile uses a multi-stage build for optimization:

1. **base**: Base image with system dependencies
2. **dependencies**: Installs Python packages
3. **production**: Final production image (minimal size)
4. **development**: Development image with extra tools

This results in a smaller final image and faster builds.

## Troubleshooting

### Port Already in Use:
If port 5000 is already in use, change it:
```bash
docker run -d -p 8080:5000 --name air-drums air-drums:latest
```

### Container Won't Start:
Check logs for errors:
```bash
docker logs air-drums
```

### Permission Issues:
The container runs as non-root user (appuser) for security. If you encounter permission issues:
```bash
docker exec -it air-drums bash
# Then check file permissions inside container
```

### Rebuild After Code Changes:
Always rebuild after making changes:
```bash
docker-compose up --build
```

## Production Deployment

For production, consider:

1. **Use a Production WSGI Server**: Modify Dockerfile to use Gunicorn:
   ```dockerfile
   CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
   ```

2. **Add Reverse Proxy**: Use Nginx in front of the Flask app

3. **Enable HTTPS**: Configure SSL/TLS certificates

4. **Set Resource Limits**: Add memory and CPU limits in docker-compose.yml

5. **Use Environment Secrets**: Use Docker secrets or environment files for sensitive data

## Image Size Optimization

The multi-stage build already optimizes the image size. Current optimizations:
- Using Python slim base image
- Removing apt cache after installations
- Using --no-cache-dir for pip
- Multi-stage build to exclude build dependencies

## Health Checks

The container includes a health check that verifies the application is responding:
```bash
docker inspect --format='{{.State.Health.Status}}' air-drums
```

## Next Steps

- [ ] Set up CI/CD pipeline
- [ ] Configure production WSGI server (Gunicorn)
- [ ] Add Nginx reverse proxy
- [ ] Set up SSL/TLS
- [ ] Configure monitoring and logging

## Support

For issues or questions, check the main README.md or open an issue on the repository.

