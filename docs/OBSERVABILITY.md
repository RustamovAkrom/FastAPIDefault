# 📊 Observability — Мониторинг, Логирование и Отслеживание Ошибок

Полный гайд по настройке и использованию систем мониторинга, логирования и трекинга ошибок в FastAPI Default.

---

## 🎯 Три столпа Observability

1. **Metrics** — числовые данные о производительности (Prometheus)
2. **Logs** — текстовые записи событий (Loki + Loguru)
3. **Traces** — полные пути выполнения запросов (Sentry)

---

## 📊 Prometheus Метрики

### Что отслеживается

**Встроенные метрики:**

```
fastapi_requests_total{method,endpoint,status}        # Всего запросов
fastapi_request_duration_seconds{method,endpoint}    # Время обработки
fastapi_request_errors_total{method,endpoint,status} # Ошибки
fastapi_requests_in_progress{app}                    # Текущих запросов
fastapi_app_info{version,env}                        # Метаданные приложения
```

### Endpoint для скрейпинга

```
GET http://localhost:8001/metrics
```

**Безопасность:** Опционально используйте `PROMETHEUS_METRICS_KEY` для ограничения доступа:

```bash
# Только с правильный ключом
curl -H "X-Metrics-Key: your-secret-key" http://localhost:8001/metrics
```

### Конфигурация Prometheus

**`deployments/prometheus/prometheus.yml`:**

```yaml
global:
  scrape_interval: 5s
  evaluation_interval: 5s

scrape_configs:
  - job_name: 'fastapi'
    static_configs:
      - targets: ['web:8000']        # Docker Compose
    metrics_path: /metrics
    scrape_interval: 5s

  # (Опционально) Собирать метрики из других источников
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
```

### Доступ к Prometheus UI

**URL:** http://localhost:9090

**Функции:**
- Query metrics в real-time
- Просмотр target статусов
- Debuggинг alert rules

### PromQL Queries (примеры)

```promql
# RPS (requests per second) за последние 5 минут
rate(fastapi_requests_total[5m])

# P95 latency
histogram_quantile(0.95, fastapi_request_duration_seconds)

#  Error rate (%)
rate(fastapi_request_errors_total[5m]) * 100

# Requests in progress
fastapi_requests_in_progress

# Slow requests (>1s)
fastapi_request_duration_seconds > 1
```

---

## 📈 Grafana Dashboards

### Встроенные Dashboards

1. **FastAPI Metrics** — основные метрики приложения
2. **Infrastructure** — CPU, Memory, Disk, Network

### Доступ

**URL:** http://localhost:3000  
**Логин:** admin  
**Пароль:** admin  

⚠️ **Меняйте пароль в production!**

### Создать custom dashboard

1. Откройте Grafana
2. Create → Dashboard
3. Add Panel → Prometheus
4. Используйте PromQL queries из примеров выше
5. Save

### Пример User-friendly Dashboard

```json
{
  "title": "API Health",
  "panels": [
    {
      "title": "Requests per second",
      "targets": [{"expr": "rate(fastapi_requests_total[5m])"}]
    },
    {
      "title": "Error Rate (%)",
      "targets": [{"expr": "rate(fastapi_request_errors_total[5m]) * 100"}]
    },
    {
      "title": "P95 Latency (ms)",
      "targets": [{"expr": "histogram_quantile(0.95, fastapi_request_duration_seconds) * 1000"}]
    },
    {
      "title": "Database Connections",
      "targets": [{"expr": "fastapi_db_connections"}]
    }
  ]
}
```

---

## 📝 Логирование (Loguru + Loki)

### Loguru Конфигурация

**`src/core/logger.py`:**

```python
from loguru import logger

# Удалить стандартный обработчик
logger.remove()

# Добавить консоль
logger.add(
    sys.stdout,
    level=level,
    format="<green>{time}</green> | <level>{level}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
    colorize=True
)

# Добавить файл (JSON в production)
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="10 days",
    serialize=True  # JSON format в production
)

# Отдельный файл для ошибок
logger.add(
    "logs/errors.log",
    level="ERROR",
    rotation="5 MB",
    retention="30 days",
    compress="zip"
)
```

### Использование в коде

```python
from core.logger import logger

logger.debug("Отладочное сообщение")
logger.info("Информационное сообщение")
logger.warning("Предупреждение")
logger.error("Ошибка")
logger.critical("Критическая ошибка", user_id=123, action="payment")
```

### Loki для сбора логов (Docker)

**`deployments/loki/promtail.yml`:**

```yaml
server:
  http_listen_port: 9080

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: docker-containers
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
    relabel_configs:
      - source_labels: ['__meta_docker_container_name']
        target_label: 'container'
      - source_labels: ['__meta_docker_container_label_com_docker_compose_service']
        target_label: 'service'
```

### Loki UI (через Grafana)

1. Откройте Grafana
2. Explore → Select Loki data source
3. Используйте LogQL для поиска логов:

```logql
# Все логи от сервиса web
{service="web"}

# Только ERROR логи
{service="web"} | json | level = "ERROR"

# Логи от пользователя
{service="web"} | json | user_id = "123"

# Распределение по уровням
sum by (level) (count_over_time({service="web"} | json [5m]))
```

---

## 🔔 Sentry Error Tracking

### Что отслеживает Sentry

- ✅ Необработанные исключения (500 errors)
- ✅ Стэк-трейсы с контекстом
- ✅ Performance monitoring (трассировки)
- ✅ Release tracking и deploy notifications
- ✅ User feedback

### Включение Sentry

1. Создайте аккаунт на [sentry.io](https://sentry.io)
2. Создайте проект для FastAPI
3. Скопируйте DSN
4. Добавьте в `.env`:

```env
SENTRY_DSN=https://key@sentry.io/1234567
SENTRY_TRACES_SAMPLE_RATE=0.1     # 10% запросов для трассировки
```

5. Приложение автоматически инициализирует Sentry при старте

### Инициализация в коде

**`src/core/sentry.py`:**

```python
import sentry_sdk

def init_sentry() -> None:
    settings = get_settings()
    
    if not settings.sentry_dsn:
        return
    
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.env,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        send_default_pii=True,
        debug=settings.debug,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ]
    )
```

### Sentry UI Features

**Groups** — группирование однотипных ошибок  
**Releases** — отслеживание по версиям  
**Performance** — трассировки и bottlenecks  
**Alerts** — уведомления при критических ошибках  

### Пример alert rule

```
When an event has:
  - level = error
  - (environment = production)
  - (error.value = "500")

Alert every 15 minutes to Slack #errors channel
```

---

## 🏥 Health Checks

### Встроенные endpoints

**`GET /healthcheck`**
```json
{
  "timestamp": 1677880800
}
```

**`GET /status`**
```json
{
  "app": "ok"
}
```

**`GET /version`**
```json
{
  "version": "1.0.0"
}
```

### Использование в Kubernetes

```yaml
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
```

---

## 🚨 Alerting Rules (Prometheus)

### Рекомендуемые alerts

**`deployments/prometheus/alerts.yml`:**

```yaml
groups:
  - name: fastapi_alerts
    interval: 30s
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: |
          (
            rate(fastapi_request_errors_total[5m]) /
            rate(fastapi_requests_total[5m])
          ) > 0.05
        for: 5m
        annotations:
          summary: "High error rate on {{ $labels.endpoint }}"
          description: "Error rate is {{ $value | humanizePercentage }}"

      # High latency
      - alert: HighLatency
        expr: |
          histogram_quantile(0.95, fastapi_request_duration_seconds) > 1.0
        for: 5m
        annotations:
          summary: "High latency on {{ $labels.endpoint }}"
          description: "P95 latency is {{ $value | humanizeDuration }}"

      # Service down
      - alert: ServiceDown
        expr: up == 0
        for: 1m

      # Database unreachable
      - alert: DatabaseDown
        expr: pg_up == 0
        for: 2m
```

### Настройка Alertmanager

```yaml
global:
  slack_api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'

route:
  receiver: 'slack-errors'
  group_by: ['alertname', 'service']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 12h

receivers:
  - name: 'slack-errors'
    slack_configs:
      - channel: '#alerts'
        title: 'Alert: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

---

## 🔍 Debugging & Troubleshooting

### Проверить метрики

```bash
# Скачать метрики human-readable формате
curl http://localhost:8001/metrics | grep fastapi_requests_total
```

### Проверить логи

```bash
# Локально
tail -f logs/app.log

# Docker
docker compose logs -f web
```

### Проверить Sentry

```bash
# Тестовое исключение
curl "http://localhost:8001/api/nonexistent"

# Проверить в Sentry UI в консоли браузера
```

### Perf profiling

```python
# Используйте встроенный Sentry profiler
import sentry_sdk

with sentry_sdk.profiler.profile() as prof:
    # Код для профилирования
    do_something()
    
# Profile автоматически отправляется в Sentry
```

---

## 📈 Best Practices

✅ **Metrics Cardinality:** Не используйте high-cardinality значения в labels  
✅ **Log Level:** INFO в dev, WARNING в production  
✅ **Sample Rate:** 100% в dev, 10-50% в production (для performance)  
✅ **Retention:** 10 дней для логов, 30+ дней для метрик  
✅ **Alerts:** Настраивайте, чтобы избежать alert fatigue  
✅ **Dashboards:** Сделайте их доступными для всей команды  

---

## 📚 Дополнительные ресурсы

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Sentry Documentation](https://docs.sentry.io/)
- [Loguru Documentation](https://loguru.readthedocs.io/)
- [Loki Documentation](https://grafana.com/docs/loki/)

---

## 🔗 Связанная документация

- [**ARCHITECTURE.md**](ARCHITECTURE.md) — Архитектура приложения
- [**DEPLOYMENT.md**](DEPLOYMENT.md) — Production деплой
