import json
from pathlib import Path
from .models import LearningConsent

class LearningStore:
    def __init__(self,root):
        self.root=Path(root); d=self.root/".berkios"; d.mkdir(parents=True,exist_ok=True)
        self.path=d/"learning_dataset.json"; self.consent_path=d/"learning_consent.json"
    def consent(self):
        if not self.consent_path.exists(): return LearningConsent()
        return LearningConsent(**json.loads(self.consent_path.read_text(encoding="utf-8")))
    def set_consent(self,consent):
        self.consent_path.write_text(json.dumps(consent.__dict__,indent=2),encoding="utf-8")
    def add(self,example):
        if example.consent_required and not self.consent().enabled:
            raise PermissionError("learning consent is not enabled")
        rows=self.list(); rows.append(example.to_dict())
        self.path.write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding="utf-8")
        return example
    def list(self):
        if not self.path.exists(): return []
        return json.loads(self.path.read_text(encoding="utf-8"))
    def export_jsonl(self,destination):
        p=Path(destination); p.write_text(
            "".join(json.dumps(x,ensure_ascii=False)+"\n" for x in self.list()),
            encoding="utf-8")
        return p
