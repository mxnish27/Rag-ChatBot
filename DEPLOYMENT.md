# Deployment Guide

Complete guide for deploying the RAG Course Chatbot to production environments.

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Production Best Practices](#production-best-practices)
5. [Monitoring and Maintenance](#monitoring-and-maintenance)
6. [Scaling Strategies](#scaling-strategies)

## Pre-Deployment Checklist

### Security

- [ ] Change default API keys
- [ ] Enable API authentication (`API_KEY_ENABLED=True`)
- [ ] Configure CORS origins for production domains
- [ ] Use HTTPS/SSL certificates
- [ ] Set strong passwords for Redis
- [ ] Review file upload restrictions
- [ ] Enable rate limiting

### Configuration

- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=False`
- [ ] Configure production vector store (Pinecone recommended)
- [ ] Set appropriate log levels
- [ ] Configure resource limits
- [ ] Set up backup strategy

### Testing

- [ ] Test all API endpoints
- [ ] Load test with expected traffic
- [ ] Test document upload and processing
- [ ] Verify RAG responses quality
- [ ] Test error handling
- [ ] Check health endpoints

## Docker Deployment

### Single Server Deployment

#### Step 1: Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Step 2: Clone and Configure

```bash
# Clone repository
git clone <repository-url>
cd rag-course-chatbot

# Create production environment file
cp .env.example .env
nano .env
```

**Production `.env` settings:**
```env
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

# Security
API_KEY_ENABLED=True
API_KEY=your-strong-random-key-here
CORS_ORIGINS=["https://yourdomain.com"]

# Vector Store (Pinecone recommended for production)
VECTOR_STORE=pinecone
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=your-environment
PINECONE_INDEX_NAME=course-chatbot-prod

# LLM
LLM_MODEL=meta-llama/Llama-3-8B-Instruct
HUGGINGFACE_TOKEN=your-hf-token

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_REQUESTS=50
RATE_LIMIT_PERIOD=60

# Redis
REDIS_PASSWORD=your-redis-password
```

#### Step 3: Deploy

```bash
# Build and start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

#### Step 4: Set Up Reverse Proxy (Nginx)

```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/rag-chatbot
```

**Nginx configuration:**
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for long-running requests
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Frontend
    location / {
        proxy_pass http://localhost:3000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # File upload size limit
    client_max_body_size 50M;
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/rag-chatbot /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

#### Step 5: Set Up SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is set up automatically
```

### Docker Swarm Deployment (Multi-Server)

#### Initialize Swarm

```bash
# On manager node
docker swarm init --advertise-addr <MANAGER-IP>

# On worker nodes (use token from init output)
docker swarm join --token <TOKEN> <MANAGER-IP>:2377
```

#### Create Stack File

**docker-stack.yml:**
```yaml
version: '3.8'

services:
  rag-chatbot:
    image: your-registry/rag-chatbot:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
    secrets:
      - api_key
      - pinecone_key
    volumes:
      - data:/app/data

  redis:
    image: redis:7-alpine
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager
    volumes:
      - redis-data:/data

  frontend:
    image: nginx:alpine
    deploy:
      replicas: 2
    ports:
      - "3000:80"
    volumes:
      - ./frontend:/usr/share/nginx/html:ro

volumes:
  data:
  redis-data:

secrets:
  api_key:
    external: true
  pinecone_key:
    external: true
```

#### Deploy Stack

```bash
# Create secrets
echo "your-api-key" | docker secret create api_key -
echo "your-pinecone-key" | docker secret create pinecone_key -

# Deploy stack
docker stack deploy -c docker-stack.yml rag-chatbot

# Check services
docker stack services rag-chatbot
```

## Cloud Deployment

### AWS Deployment

#### Option 1: EC2 Instance

**1. Launch EC2 Instance:**
- AMI: Ubuntu 22.04 LTS
- Instance Type: t3.xlarge (minimum) or g4dn.xlarge (with GPU)
- Storage: 50GB+ EBS volume
- Security Group: Allow ports 80, 443, 22

**2. Connect and Deploy:**
```bash
# SSH to instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Follow Docker deployment steps above
```

**3. Set Up Elastic IP:**
```bash
# Allocate and associate Elastic IP in AWS Console
```

#### Option 2: ECS (Elastic Container Service)

**1. Create ECR Repository:**
```bash
aws ecr create-repository --repository-name rag-chatbot
```

**2. Build and Push Image:**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and tag
docker build -t rag-chatbot .
docker tag rag-chatbot:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-chatbot:latest

# Push
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-chatbot:latest
```

**3. Create ECS Task Definition:**
```json
{
  "family": "rag-chatbot",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "8192",
  "containerDefinitions": [
    {
      "name": "rag-chatbot",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-chatbot:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/rag-chatbot",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

**4. Create ECS Service with Load Balancer**

#### Option 3: Lambda + API Gateway (Serverless)

**Note:** Requires modifications for cold start optimization and model loading.

### Google Cloud Platform

#### Cloud Run Deployment

**1. Build and Push to GCR:**
```bash
# Configure gcloud
gcloud auth configure-docker

# Build
docker build -t gcr.io/your-project/rag-chatbot .

# Push
docker push gcr.io/your-project/rag-chatbot
```

**2. Deploy to Cloud Run:**
```bash
gcloud run deploy rag-chatbot \
  --image gcr.io/your-project/rag-chatbot \
  --platform managed \
  --region us-central1 \
  --memory 8Gi \
  --cpu 4 \
  --timeout 300 \
  --set-env-vars ENVIRONMENT=production \
  --set-secrets API_KEY=api-key:latest
```

### Azure Deployment

#### Azure Container Instances

```bash
# Create resource group
az group create --name rag-chatbot-rg --location eastus

# Create container
az container create \
  --resource-group rag-chatbot-rg \
  --name rag-chatbot \
  --image your-registry/rag-chatbot:latest \
  --cpu 4 \
  --memory 8 \
  --ports 8000 \
  --environment-variables ENVIRONMENT=production \
  --secure-environment-variables API_KEY=your-key
```

### Heroku Deployment

**1. Create Heroku App:**
```bash
heroku create your-app-name
```

**2. Add Buildpack:**
```bash
heroku buildpacks:set heroku/python
```

**3. Set Config Vars:**
```bash
heroku config:set ENVIRONMENT=production
heroku config:set API_KEY=your-key
heroku config:set VECTOR_STORE=pinecone
heroku config:set PINECONE_API_KEY=your-pinecone-key
```

**4. Deploy:**
```bash
git push heroku main
```

**5. Scale:**
```bash
heroku ps:scale web=1:standard-2x
```

## Production Best Practices

### 1. Environment Configuration

```env
# Production settings
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

# Security
API_KEY_ENABLED=True
API_KEY=<strong-random-key>
CORS_ORIGINS=["https://yourdomain.com"]

# Performance
API_WORKERS=4
REDIS_HOST=redis
REDIS_PASSWORD=<strong-password>
```

### 2. Resource Limits

**Docker Compose:**
```yaml
services:
  rag-chatbot:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G
```

### 3. Logging

```python
# Configure structured logging
LOG_FORMAT=json
LOG_LEVEL=INFO

# Use log aggregation service
# - CloudWatch (AWS)
# - Stackdriver (GCP)
# - Application Insights (Azure)
```

### 4. Monitoring

**Health Checks:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s
```

**Metrics to Monitor:**
- Request rate and latency
- Error rate
- Memory usage
- CPU usage
- Vector store query time
- LLM inference time

### 5. Backup Strategy

**Vector Store:**
```bash
# Pinecone: Automatic backups included
# Chroma: Regular backups needed

# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf backup_$DATE.tar.gz data/chroma_db/
aws s3 cp backup_$DATE.tar.gz s3://your-backup-bucket/
```

### 6. Secrets Management

**AWS Secrets Manager:**
```bash
aws secretsmanager create-secret \
  --name rag-chatbot/api-key \
  --secret-string "your-api-key"
```

**Docker Secrets:**
```bash
echo "your-secret" | docker secret create api_key -
```

### 7. Rate Limiting

```env
RATE_LIMIT_ENABLED=True
RATE_LIMIT_REQUESTS=50
RATE_LIMIT_PERIOD=60
```

Consider using:
- Redis for distributed rate limiting
- API Gateway rate limiting
- CDN rate limiting

## Monitoring and Maintenance

### Monitoring Setup

**1. Application Metrics:**
```python
# Add Prometheus metrics
from prometheus_client import Counter, Histogram

request_count = Counter('requests_total', 'Total requests')
request_duration = Histogram('request_duration_seconds', 'Request duration')
```

**2. Log Aggregation:**
```bash
# Use ELK Stack, Datadog, or cloud-native solutions
```

**3. Alerting:**
- Set up alerts for high error rates
- Monitor resource usage
- Track response times
- Alert on health check failures

### Maintenance Tasks

**Regular Updates:**
```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Rebuild Docker image
docker-compose build --no-cache

# Rolling update
docker-compose up -d --no-deps --build rag-chatbot
```

**Database Maintenance:**
```bash
# Optimize vector store
# Clean old logs
find logs/ -name "*.log" -mtime +30 -delete

# Monitor disk usage
df -h
```

## Scaling Strategies

### Horizontal Scaling

**1. Load Balancing:**
```nginx
upstream rag_backend {
    least_conn;
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

**2. Auto-Scaling (Kubernetes):**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: rag-chatbot-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: rag-chatbot
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Vertical Scaling

- Increase instance size
- Add GPU for faster inference
- Increase memory for larger models

### Caching Strategy

**1. Response Caching:**
```python
# Cache frequent queries in Redis
CACHE_TTL=3600  # 1 hour
```

**2. Model Caching:**
```python
# Cache loaded models
# Use model quantization
# Implement model serving layer
```

### Performance Optimization

**1. Model Optimization:**
- Use quantization (4-bit/8-bit)
- Implement model distillation
- Use smaller embedding models

**2. Vector Store Optimization:**
- Tune index parameters
- Use approximate search
- Implement result caching

**3. API Optimization:**
- Enable compression
- Implement request batching
- Use async processing

## Troubleshooting Production Issues

### High Memory Usage

```bash
# Check memory
docker stats

# Reduce model size
LLM_MODEL=meta-llama/Llama-3-8B-Instruct

# Enable quantization
load_in_8bit=True
```

### Slow Response Times

```bash
# Check bottlenecks
# - Vector store query time
# - LLM inference time
# - Network latency

# Solutions:
# - Add caching
# - Use GPU
# - Optimize retrieval
```

### Connection Issues

```bash
# Check service health
docker-compose ps

# Check logs
docker-compose logs rag-chatbot

# Restart services
docker-compose restart
```

## Security Checklist

- [ ] HTTPS enabled
- [ ] API authentication enabled
- [ ] Strong passwords set
- [ ] CORS properly configured
- [ ] File upload validation
- [ ] Rate limiting enabled
- [ ] Secrets not in code
- [ ] Regular security updates
- [ ] Firewall configured
- [ ] Monitoring enabled

## Cost Optimization

**1. Use Spot Instances (AWS):**
- 70-90% cost savings
- Good for non-critical workloads

**2. Right-Size Resources:**
- Monitor actual usage
- Scale down during off-hours

**3. Use Reserved Instances:**
- 30-70% savings for predictable workloads

**4. Optimize Vector Store:**
- Use free tier when possible
- Clean up unused data

---

**Your RAG chatbot is now production-ready! 🚀**

For support, refer to:
- [README.md](README.md) - General documentation
- [SETUP.md](SETUP.md) - Setup instructions
- API docs at `/docs` endpoint
