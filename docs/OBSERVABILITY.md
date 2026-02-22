# 📊 Observability Guide

Production-grade monitoring stack:

- Prometheus (metrics)
- Grafana (dashboards)
- Sentry (error tracking)

---

# 1. Sentry

Purpose:

- Capture exceptions
- Stack traces
- Performance traces
- User context

Enabled via:

```

SENTRY_DSN=

```

Initialization:

```

core/sentry.py

```

Captured automatically:

- Unhandled exceptions
- ASGI errors
- Middleware errors

---

# 2. Prometheus

Metrics endpoint:

```

/metrics

```

Exposes:

- HTTP request count
- Latency histogram
- Error counters
- Python runtime metrics

Middleware:

```

core/prometheus.py

```

---

# 3. Grafana

Access:

```

[http://localhost:3000](http://localhost:3000)

```

Uses Prometheus datasource.

Recommended dashboards:

- RPS
- p95 latency
- error rate
- endpoint distribution

---

# 4. Metrics Best Practices

- Avoid high cardinality labels
- Normalize endpoints
- Track 4xx and 5xx separately
- Monitor DB latency

---

# 5. Production Alerts (Planned)

Future:

- Alert if error rate > 5%
- Alert if latency > 1s
- Alert if service down

---

# 6. Health Endpoints

```

/healthcheck
/status
/version

```

Used for load balancers and uptime checks.
