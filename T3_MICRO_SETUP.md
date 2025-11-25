# T3.micro Deployment Guide

## Requirements
- AWS t3.micro instance (1 vCPU, 1GB RAM)
- Ubuntu 22.04 LTS
- Domain pointing to instance IP (optional)

## 1. Launch EC2 Instance

```bash
# AMI: Ubuntu 22.04 LTS
# Type: t3.micro
# Storage: 20GB gp3
# Security Group:
#   - SSH (22) from your IP
#   - HTTP (80) from anywhere
#   - HTTPS (443) from anywhere
```

## 2. Initial Server Setup

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Update
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker ubuntu
newgrp docker

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Verify
docker --version
docker compose version
```

## 3. Clone and Configure

```bash
# Clone repo
git clone https://github.com/Jasuni69/binko.ai.git
cd binko.ai

# Create production env file
cp .env.prod.example .env.prod
nano .env.prod
```

Fill in `.env.prod`:
```
POSTGRES_USER=binko
POSTGRES_PASSWORD=<generate-strong-password>
POSTGRES_DB=binko
OPENAI_API_KEY=sk-your-key
CORS_ORIGINS=http://your-instance-ip
```

## 4. Deploy

```bash
chmod +x deploy.sh
./deploy.sh
```

## 5. Verify

```bash
# Check containers
docker compose -f docker-compose.prod.yml ps

# Check logs
docker compose -f docker-compose.prod.yml logs -f

# Test API
curl http://localhost/health
```

## Resource Usage (t3.micro)

Expected usage with light traffic:
- RAM: ~600-700MB (Postgres ~200MB, Backend ~150MB, Frontend ~50MB, Nginx ~20MB)
- CPU: Low except during AI generation
- Disk: ~2-3GB for Docker images

## Scaling Notes

If you outgrow t3.micro:
1. **t3.small** (2GB RAM) - Handles more concurrent users
2. **Separate DB** - Move Postgres to RDS
3. **Add Redis** - For caching and rate limiting

## Troubleshooting

### Out of memory
```bash
# Check memory
free -h

# Add swap (if not present)
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Container keeps restarting
```bash
docker compose -f docker-compose.prod.yml logs backend
```

### Database connection issues
```bash
# Check if postgres is healthy
docker compose -f docker-compose.prod.yml exec db pg_isready
```

## Updates

```bash
cd binko.ai
git pull
./deploy.sh
```
