from pathlib import Path
from datetime import datetime, timezone
import json, re

class ErrorHistory:
    """Mémoire persistante des erreurs, diagnostics et corrections."""
    def __init__(self, workspace):
        self.path=Path(workspace)/".berkios"/"error_history.json"
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.items=self._load()

    def _load(self):
        if self.path.exists():
            try: return json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError: return []
        return []

    def _save(self):
        self.path.write_text(json.dumps(self.items,indent=2,ensure_ascii=False),encoding="utf-8")

    def remember(self,error,diagnosis=None,files=None,proposal=None,
                 verification=None,run_id=None):
        item={
            "id": f"errmem-{len(self.items)+1}",
            "error_id": error.id,
            "run_id": run_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "message": error.message,
            "kind": error.kind.value,
            "severity": error.severity.value,
            "source": error.source,
            "file": error.file,
            "line": error.line,
            "column": error.column,
            "code": error.code,
            "diagnosis": diagnosis or {},
            "files": files or ([error.file] if error.file else []),
            "proposal": proposal or {},
            "verification": verification or {},
            "status": "observed"
        }
        self.items.append(item); self._save()
        return item

    def mark_corrected(self, history_id, files=None, proposal=None,
                       verification=None, run_id=None):
        item=self.get(history_id)
        item["status"]="corrected"
        item["corrected_at"]=datetime.now(timezone.utc).isoformat()
        if files is not None: item["files"]=files
        if proposal is not None: item["proposal"]=proposal
        if verification is not None: item["verification"]=verification
        if run_id is not None: item["correction_run_id"]=run_id
        self._save()
        return item

    def get(self, history_id):
        return next(x for x in self.items if x["id"]==history_id)

    def list(self, limit=100):
        return self.items[-limit:]

    def search(self, query, file=None):
        q=query.lower()
        results=[]
        for item in reversed(self.items):
            hay=" ".join(str(item.get(k,"")) for k in
                         ("message","kind","file","code","diagnosis","files","proposal"))
            if q in hay.lower() and (file is None or file in (item.get("files") or [])):
                results.append(item)
        return results

    def similar(self,error):
        terms=set(re.findall(r"[a-zA-Z_][a-zA-Z0-9_]{3,}",error.message.lower()))
        scored=[]
        for item in self.items:
            hay=(str(item.get("message",""))+" "+str(item.get("diagnosis",""))).lower()
            score=sum(1 for t in terms if t in hay)
            if item.get("kind")==error.kind.value: score+=2
            if error.file and item.get("file")==error.file: score+=3
            if score: scored.append((score,item))
        scored.sort(key=lambda x:(x[0],x[1].get("created_at","")),reverse=True)
        return [x[1] for x in scored[:10]]
