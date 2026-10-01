# Berkios 5.17 — Codix Multi-Teacher

Berkios 5.17 introduces multi-teacher comparison.

## Flow

```text
              ┌─ OpenAI
Task ─────────┼─ Claude
              ├─ Gemini
              └─ Local model
                    │
                    ▼
             TeacherComparison
                    │
          ┌─────────┴─────────┐
          │                   │
     agreement            divergence
          │                   │
          ▼                   ▼
    candidate         human review / synthesis
          │                   │
          └─────────┬─────────┘
                    ▼
          Codix Training Pipeline
```

## Safety and provenance

A majority or agreement does **not** automatically make an answer training data.
The selected output remains a candidate and must follow Codix consent, review,
curation and evaluation.

When teachers disagree, the engine does not silently concatenate their answers.
An explicit synthesis can be attached with a rationale and the source sample IDs.

## Teacher roles

Teachers are interchangeable providers. Codix remains the target intelligence;
it is not identified with any one provider.
