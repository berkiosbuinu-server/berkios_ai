from __future__ import annotations
from pathlib import Path
import json
from .models import ModelRecord

class CodixModelRegistry:
    """Persistent registry for candidate, validated and active Codix versions."""

    def __init__(self, root=".berkios/model_registry"):
        self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True)
        self.path=self.root/"registry.json"
        self.records={}
        self.active=None
        self._load()

    def _load(self):
        if not self.path.exists(): return
        try:
            d=json.loads(self.path.read_text(encoding="utf-8"))
            self.records=d.get("records",{}); self.active=d.get("active")
        except Exception: pass

    def _save(self):
        self.path.write_text(json.dumps(
            {"active":self.active,"records":self.records},
            ensure_ascii=False,indent=2),encoding="utf-8")

    def register(self, record: ModelRecord):
        self.records[record.version]=record.__dict__.copy()
        self._save()
        return record

    def get(self, version):
        d=self.records.get(version)
        return ModelRecord(**d) if d else None

    def promote(self, version):
        record=self.get(version)
        if not record: raise KeyError(version)
        if record.status!="validated": raise ValueError("Only validated models can be promoted.")
        record.status="active"
        self.records[version]=record.__dict__.copy()
        self.active=version
        self._save()
        return record

    def list(self):
        return list(self.records.values())

    def active_model(self):
        return self.get(self.active) if self.active else None
