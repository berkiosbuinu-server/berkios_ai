# Berkios 4.0 — Self-Learning Correction Loop

Berkios 4.0 learns from **validated** repairs.

## Rule

A correction is recorded only when verification explicitly reports:

```json
{"success": true}
```

Learned corrections are contextual knowledge. They never auto-approve a future change.

## Capture

Conceptual endpoint:

`POST /v1/corrections/capture`

Example payload:

```json
{
  "message": "ImportError: missing module",
  "error_id": "err-123",
  "run_id": "run-456",
  "diagnosis": {"cause": "dependency missing"},
  "proposal": {"files": ["src/app.py"]},
  "verification": {"success": true, "command": "python -m pytest"},
  "files": ["src/app.py"],
  "symbols": ["main"],
  "git_commit": "abc123",
  "git_branch": "main"
}
```

## Recall

Conceptual endpoint:

`GET /v1/corrections/relevant`

Search uses the current error message, affected files and symbols.

## Event

Successful capture emits:

`correction.recorded`

This event can be consumed by iBook to refresh the AI/context panels.
