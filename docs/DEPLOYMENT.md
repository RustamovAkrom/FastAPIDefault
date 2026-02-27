# 🚀 Deployment Guide — Production Готовность

Полный гайд по развёртыванию FastAPI Default на production и настройке инфраструктуры для high-availability приложений.

---

## 📋 Требования

- **Docker** 20.10+ и **Docker Compose** 2.0+
- **PostgreSQL** 14+ (управляемая служба или self-hosted)
- **SSL/TLS** сертификаты (Let's Encrypt или другой провайдер)
- **DNS** записи указывающие на ваш сервер
- **Reverse Proxy** (Nginx, Traefik или другой)

---

## 🔧 Конфигурация перед деплоем

### 1️⃣ Подготовьте переменные окружения

**Production `.env` пример:**

```env
# Environment
ENV=prod
DEBUG=false
SECRET_KEY=your-super-secret-key-change-this

# Database
POSTGRES_HOST=db.example.com        # Удаленная БД
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=very-secure-password
POSTGRES_DB=production_db
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# Application
APP_TITLE="My API"
ROOT_PATH=/api

# Security
ALLOWED_HOSTS=api.example.com,www.api.example.com
CORS_ORIGINS=https://example.com,https://app.example.com

# Monitoring
PROMETHEUS_ENABLED=true
PROMETHEUS_METRICS_KEY=your-secret-metrics-key

# Error Tracking
SENTRY_DSN=https://key@sentry.io/1234567
SENTRY_TRACES_SAMPLE_RATE=0.1        # 10% трассировки

# Logging
LOG_LEVEL=WARNING
LOG_JSON=true                        # JSON в production
LOG_TO_FILE=true
LOG_FILE_PATH=/var/log/app/app.log

# Admin
ADMIN_ENABLED=true
ADMIN_PATH=/admin
```

**Безопасность:**
- ❌ Никогда не коммитьте `.env` файл
- ✅ Используйте GitHub Secrets или secret manager (AWS Secrets Manager, HashiCorp Vault)
- ✅ Ротируйте ключи регулярно
- ✅ Используйте разные ключи для dev/prod

### 2️⃣ Подготовьте сертификаты SSL/TLS

**Опция 1: Let's Encrypt с Certbot**

```bash
# Установить certbot
sudo apt-get install certbot python3-certbot-nginx

# Получить сертификат (для Nginx)
sudo certbot certonly --nginx -d api.example.com -d www.api.example.com

# Сертификаты загружены в /etc/letsencrypt/live/api.example.com/
```

**Опция 2: AWS Certificate Manager (если на AWS)**

```bash
# Создать сертификат через AWS Console
# Используется автоматически для ALB/CloudFront
```

---

## 🐳 Docker Production Setup

### Multi-stage Dockerfile (использующийся)

Наш Dockerfile уже оптимизирован для production:

```dockerfile
Stage 1: Builder        # Собирает зависимости
Stage 2: Runtime       # Минимальный runtime образ
```

**Размер образа:** ~400MB (с Python 3.11 и зависимостями)

### Сборка и публикация образа

```bash
# Собрать образ локально
docker build -t myapi:1.0.0 -f deployments/compose/backend/Dockerfile .

# Пометить для реестра
docker tag myapi:1.0.0 registry.example.com/myapi:1.0.0
docker tag myapi:1.0.0 registry.example.com/myapi:latest

# Загрузить в реестр (Docker Hub, ECR, GitLab Registry и т.д.)
docker push registry.example.com/myapi:1.0.0
docker push registry.example.com/myapi:latest
```

---

## 🌐 Nginx Reverse Proxy Конфигурация

**`/etc/nginx/sites-available/api.example.com`:**

```nginx
upstream fastapi {
    # Несколько инстансов приложения для load balancing
    server web1:8000;
    server web2:8000;
    server web3:8000;
    
    # Используйте least connections
    least_conn;
}

# HTTP → HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name api.example.com www.api.example.com;
    
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name api.example.com www.api.example.com;
    
    # SSL сертификаты
    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css text/xml text/javascript 
               application/x-javascript application/json;
    gzip_min_length 1000;
    
    # Client body size
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://fastapi;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health check endpoint (не логируем)
    location /healthcheck {
        proxy_pass http://fastapi;
        access_log off;
    }
    
    # Metrics endpoint (ограничиваем доступ)
    location /metrics {
        proxy_pass http://fastapi;
        allow 10.0.0.0/8;          # Internal network only
        deny all;
    }
}
```

Активировать конфиг:

```bash
sudo ln -s /etc/nginx/sites-available/api.example.com /etc/nginx/sites-enabled/
sudo nginx -t          # Проверить синтаксис
sudo systemctl reload nginx
```

---

## 📦 Docker Compose для Production

**`docker-compose.prod.yml`:**

```yaml
version: '3.9'

services:
  web:
    image: registry.example.com/myapi:1.0.0
    container_name: api-web
    restart: always
    networks:
      - backend
    environment:
      ENV: prod
      WORKERS: 4
    env_file: .env.prod
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/healthcheck"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    logging:
      driver: "json-file"
      options:
        max-size: "200m"
        max-file: "10"

  postgres:
    image: postgres:16-alpine
    container_name: api-postgres
    restart: always
    networks:
      - backend
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: always
    networks:
      - backend
    volumes:
      - ./deployments/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: always
    networks:
      - backend
    environment:
      GF_SECURITY_ADMIN_USER: admin
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./deployments/grafana/provisioning:/etc/grafana/provisioning:ro

volumes:
  postgres_data:
    driver: local
  prometheus_data:
    driver: local
  grafana_data:
    driver: local

networks:
  backend:
    driver: bridge
```

**Запустить.**

```bash
docker compose -f docker-compose.prod.yml up -d
```

---

## 🔄 Database Миграции

### Автоматические миграции при старте

Модифицируйте `entrypoint` или `start` скрипт для автоматического запуска миграций:

```bash
#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
pg_isready -h ${POSTGRES_HOST} -U ${POSTGRES_USER}

echo "Running migrations..."
alembic -c src/alembic.ini upgrade head

echo "Starting application..."
exec uvicorn app:create_app --factory --workers 4 --host 0.0.0.0 --port 8000
```

### Бэкапирование БД

```bash
# Полный бэкап
pg_dump -U postgres -h localhost production_db | gzip > backup_$(date +%Y%m%d).sql.gz

# Восстановление
gunzip < backup_20260227.sql.gz | psql -U postgres -h localhost production_db

# Автоматизировать через cron
0 2 * * * /usr/local/bin/backup_db.sh     # Каждый день в 02:00
```

---

## 📊 Мониторинг и Alerting

### Prometheus Alerting Rules

**`deployments/prometheus/alerts.yml`:**

```yaml
groups:
  - name: fastapi_alerts
    rules:
      - alert: HighErrorRate
        expr: |
          rate(fastapi_request_errors_total[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }}"

      - alert: HighLatency
        expr: |
          histogram_quantile(0.95, fastapi_request_duration_seconds) > 1.0
        for: 5m
        annotations:
          summary: "High API latency"
          description: "P95 latency is {{ $value }}s"

      - alert: PodNotHealthy
        expr: up == 0
        for: 1m
        annotations:
          summary: "Pod {{ $labels.kubernetes_pod_name }} is down"
```

---

## 🚀 Kubernetes Deployment

**`k8s/fastapi-deployment.yaml`:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi
  template:
    metadata:
      labels:
        app: fastapi
    spec:
      containers:
      - name: fastapi
        image: registry.example.com/myapi:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: ENV
          value: "prod"
        - name: WORKERS
          value: "4"
        envFrom:
        - secretRef:
            name: fastapi-secrets
        livenessProbe:
          httpGet:
            path: /healthcheck
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /healthcheck
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

**Развернуть:**

```bash
kubectl apply -f k8s/fastapi-deployment.yaml
kubectl rollout status deployment/fastapi-deployment
```

---

## 🔍 Healthchecks и Readiness Probes

Наше приложение имеет встроенные healthchecks:

- **`/healthcheck`** — возвращает `200 OK` когда приложение работает
- **`/status`** — статус сервисов
- **`/metrics`** — Prometheus метрики (ограничены по IP)

---

## 📝 CI/CD Pipeline (GitHub Actions)

**`.github/workflows/deploy.yml`:**

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build image
        run: |
          docker build -t registry.example.com/myapi:${{ github.sha }} .
          docker tag registry.example.com/myapi:${{ github.sha }} registry.example.com/myapi:latest
      
      - name: Push image
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USER }} --password-stdin
          docker push registry.example.com/myapi:${{ github.sha }}
          docker push registry.example.com/myapi:latest
      
      - name: Deploy
        run: |
          ssh -i ${{ secrets.SSH_KEY }} user@prod.example.com \
            'cd /opt/fastapi-default && docker pull registry.example.com/myapi:latest && \
            docker-compose up -d'
```

---

## 🔐 Security Checklist

- ✅ ENV=prod и DEBUG=false
- ✅ SECRET_KEY установлен на уникальное значение
- ✅ HTTPS/TLS включен
- ✅ SQL Injection protection (SQLAlchemy параметризованные запросы)
- ✅ CORS правильно настроен
- ✅ Rate limiting (опционально)
- ✅ Регулярные обновления зависимостей
- ✅ Security headers (Nginx конфиг выше)
- ✅ Регулярные бэкапы БД
- ✅ Мониторинг и alerting

---

## 🐛 Troubleshooting Production

**Приложение памбалка:**
```bash
# Проверить статус
docker compose ps
docker compose logs web

# Перезагрузить
docker compose restart web
```

**Проблемы с БД:**
```bash
# Проверить подключение
docker compose exec postgres pg_isready

# Посмотреть логи БД
docker compose logs postgres
```

**Высокий CPU/Memory:**
```bash
# Увеличить WORKERS и limits
# Проверить slow queries в PostgreSQL
EXPLAIN ANALYZE <query>;
```

---

## 📚 Дополнительные ресурсы

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL Server Setup](https://wiki.postgresql.org/wiki/Detailed_installation_guides)
- [Nginx Security Headers](https://www.nginx.com/blog/http-security-headers/)
- [Docker Best Practices](https://docs.docker.com/engine/reference/builder/)

---

## 🔗 Связанная документация

- [**ARCHITECTURE.md**](ARCHITECTURE.md) — Архитектура приложения
- [**OBSERVABILITY.md**](OBSERVABILITY.md) — Мониторинг и tracking
```
