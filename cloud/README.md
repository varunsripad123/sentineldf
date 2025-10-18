# SentinelDF Cloud - Enterprise Architecture

This directory contains the enterprise-scale components for SentinelDF Cloud.

## What's Here

- **control_plane/** - Scalable API with auth, billing, usage tracking
- **data_plane/** - Distributed worker system with job queue
- **config/** - Configuration for Redis, Postgres, S3
- **monitoring/** - Prometheus, Grafana, observability
- **deployment/** - Render scaling configuration

## Relationship to Existing Code

✅ **Keeps Working:** Your existing `api_server.py` continues to work
✅ **Extends:** New enterprise features are opt-in
✅ **Backwards Compatible:** Old SDK and API calls still work

## Quick Start

### Option 1: Keep Using Simple API (Current)
```bash
# Still works exactly as before
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

### Option 2: Use Enterprise API (New)
```bash
# New scalable version with workers
uvicorn cloud.control_plane.api:app --host 0.0.0.0 --port 8000
celery -A cloud.data_plane.worker worker --loglevel=info
```

## Migration Path

1. **Phase 1:** Deploy enterprise API alongside existing (both run)
2. **Phase 2:** Migrate users gradually
3. **Phase 3:** Deprecate old API (with notice period)

No breaking changes required!
