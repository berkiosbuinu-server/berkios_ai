from pathlib import Path
from datetime import datetime, timezone
import json

class RunMemory:
    def __init__(self, workspace, run_id):
        self.path = Path(workspace) / ".berkios" / "runs" / f"{run_id}.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.items = []
    def add(self, category, content):
        item = {"category": category, "content": content,
                "at": datetime.now(timezone.utc).isoformat()}
        self.items.append(item)
        self.path.write_text(json.dumps(self.items, indent=2, ensure_ascii=False), encoding="utf-8")
        return item
    def list(self):
        return list(self.items)
