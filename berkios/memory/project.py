import json
from pathlib import Path
from datetime import datetime, timezone

class ProjectMemory:
    def __init__(self, workspace):
        self.workspace = Path(workspace)
        self.path = self.workspace / ".berkios" / "memory.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.items = self._load()

    def _load(self):
        if self.path.exists():
            return json.loads(self.path.read_text(encoding="utf-8"))
        return []

    def add(self, category, content, source="runtime", tags=None):
        item = {"id": f"mem-{len(self.items)+1}", "category": category,
                "content": content, "source": source, "tags": tags or [],
                "created_at": datetime.now(timezone.utc).isoformat()}
        self.items.append(item)
        self.path.write_text(json.dumps(self.items, indent=2, ensure_ascii=False), encoding="utf-8")
        return item

    def list(self):
        return list(self.items)

class MemoryStore(ProjectMemory):
    pass
