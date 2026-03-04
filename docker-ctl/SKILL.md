---
name: docker-ctl
description: Simplified Docker and Docker Compose operations. Use when managing containers, images, volumes, or compose stacks without remembering complex docker CLI syntax.
---

# Docker Control (docker-ctl)

Simplified Docker operations for common tasks.

## Quick Start

```bash
# List running containers
docker-ctl ps

# Quick start a container
docker-ctl run nginx --port 8080:80

# Manage compose stacks
docker-ctl compose up

# Clean up unused resources
docker-ctl cleanup
```

## Commands

### Container Management

```bash
# List containers
docker-ctl ps                    # Running only
docker-ctl ps -a                 # All containers

# Quick run with common options
docker-ctl run nginx --port 8080:80 --name my-nginx
docker-ctl run postgres:15 --env POSTGRES_PASSWORD=secret --volume pgdata:/var/lib/postgresql/data

# Stop/Start/Restart
docker-ctl stop <container>
docker-ctl start <container>
docker-ctl restart <container>

# Remove container
docker-ctl rm <container>        # Stop and remove
docker-ctl rm <container> -f     # Force remove running

# View logs
docker-ctl logs <container>      # Last 100 lines
docker-ctl logs <container> -f   # Follow

# Execute command
docker-ctl exec <container> bash
docker-ctl exec <container> "ls -la"
```

### Image Management

```bash
# List images
docker-ctl images
docker-ctl images -d             # Include dangling

# Pull image
docker-ctl pull nginx:latest

# Remove image
docker-ctl rmi <image>

# Build with tags
docker-ctl build -t myapp:1.0 .
```

### Volume Management

```bash
# List volumes
docker-ctl volumes

# Create volume
docker-ctl volume create mydata

# Remove volume
docker-ctl volume rm mydata

# Clean unused volumes
docker-ctl volume prune
```

### Docker Compose

```bash
# Start stack
docker-ctl compose up
docker-ctl compose up -d         # Detached

# Stop stack
docker-ctl compose down
docker-ctl compose down -v       # Remove volumes too

# View logs
docker-ctl compose logs
docker-ctl compose logs -f <service>

# Scale service
docker-ctl compose scale web=3

# Validate config
docker-ctl compose config
```

### System Cleanup

```bash
# Clean everything unused
docker-ctl cleanup

# Clean specific resources
docker-ctl cleanup containers    # Stopped containers
docker-ctl cleanup images        # Dangling images
docker-ctl cleanup volumes       # Unused volumes
docker-ctl cleanup networks      # Unused networks
```

## Resources

### scripts/

- `docker_ctl.py` - Main CLI script for Docker operations
