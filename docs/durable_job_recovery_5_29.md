# Berkios 5.29 — Durable Job Recovery

## Flux

1. L'API crée le job dans PostgreSQL.
2. Le job est publié dans Redis.
3. Un worker le retire de Redis et le réclame en PostgreSQL avec un `lease_until`.
4. À la réussite, le job passe à `completed`.
5. À l'échec, il est remis en `queued` jusqu'à `max_attempts`, puis `failed`.
6. Si le worker disparaît pendant le lease, un autre worker peut récupérer le job expiré.
7. Au démarrage, les jobs `queued` persistés sont réinjectés dans Redis.

## Limite importante

Le lease protège contre la perte après crash, mais le traitement applicatif doit
rester idempotent : un crash après l'exécution réelle d'un effet externe mais
avant l'écriture `completed` peut conduire à une nouvelle tentative.
