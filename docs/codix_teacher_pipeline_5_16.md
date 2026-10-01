# Berkios 5.16 — Codix Teacher Data Pipeline

Berkios 5.16 adds a provider-neutral **Teacher layer** for Codix.

## Architecture

```text
OpenAI / Claude / Gemini / Local / Custom
                 │
                 ▼
          TeacherDataBuilder
                 │
                 ├── normalized candidate
                 ├── provenance
                 ├── tests
                 └── evaluation metadata
                 │
                 ▼
       Consent + Human Review
                 │
                 ▼
          Codix Training Pipeline
                 │
                 ▼
          Evaluation / Promote
```

## Teacher vs Codix

- **Teacher**: an external or local model that produces a candidate answer.
- **Codix**: the target software-engineering intelligence.
- A provider response is **not automatically training data**.
- Project/private context is not reusable training material without the appropriate explicit consent.
- Provider permission to process data is not the same thing as permission to retain it for Codix learning.

## Multi-teacher comparison

`TeacherDataBuilder.compare()` can collect samples from multiple providers.
Consensus is intentionally conservative: it is only reported when outputs are
identical. Divergent outputs remain candidates for human review.

## Example

```python
from berkios.learning.teacher import TeacherDataBuilder

builder = TeacherDataBuilder()

sample = builder.normalize(
    provider="openai",
    model=None,
    task="Fix the failing parser test",
    input_context="Relevant project context...",
    output="Candidate patch...",
    provenance={"source": "explicit_user_task"},
    tests=["python -m pytest tests/test_parser.py"],
)

builder.save(sample)
```

The resulting candidate still needs to enter the existing Codix consent,
review, curation, evaluation and promotion pipeline.
