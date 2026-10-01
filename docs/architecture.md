# Architecture 2.0

```text
                    iBook
                      │
                 IBookBridge
                      │
                 Berkios SDK
                      │
                 HTTP API v1
                      │
                ┌─────▼─────┐
                │AgentRuntime│
                └─────┬─────┘
          ┌────────────┼────────────┐
       Context       Agent        Memory
          │            │        project/session/run
          │       Provider/Tools
          │            │
          └──── Changes ─── Verification
```

Le point central de 2.0 est `AgentRuntime`: toutes les briques ont une composition
canonique et partagent le même workspace, contexte, providers, outils et mémoire.
