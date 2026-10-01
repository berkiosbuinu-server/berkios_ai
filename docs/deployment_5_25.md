# Berkios 5.25 — Production Foundation

This release turns the existing Berkios runtime into a deployable service stack.

## Services

- `berkios_api`: existing Berkios HTTP API, containerized.
- `berkios_worker`: background worker foundation; durable job execution is a later step.
- `berkios_postgres`: PostgreSQL 16 with persistent volume.
- `berkios_redis`: Redis 7 with AOF persistence and bounded memory.
- `berkios_nginx`: reverse proxy and ACME webroot.

## First deployment

```bash
cp .env.example .env
nano .env
docker compose build
docker compose up -d
docker compose ps
curl -i http://127.0.0.1/health
```

Expected health response:

```json
{"status":"healthy","service":"berkios-api","version":"5.25.0"}
```

## HTTPS

1. Point the Berkios API DNS record to the VPS.
2. Keep port 80 reachable for ACME.
3. Issue the certificate with Certbot using `certbot/www`.
4. Install the HTTPS server block from `nginx/https-server.conf.example`.
5. Run `docker compose exec nginx nginx -t`.
6. Restart only Nginx after the configuration validates.

## Important architectural boundary

PostgreSQL and Redis are provisioned now, but the existing Berkios runtime still has in-memory state in several subsystems. This release does **not** claim that all runtime state is durable across process restarts.

The next production work should wire:
- durable run registry,
- durable approvals,
- Redis-backed jobs/events,
- PostgreSQL persistence,
- authentication,
- rate limiting,
- secrets management,
- structured observability.

## Safety

Never commit `.env`, API keys, private keys, or Let's Encrypt material.
