from pathlib import Path
from datetime import datetime, timezone
import json, re, subprocess

class CorrectionMemory:
    """Transforme l'historique d'erreurs en connaissances de correction réutilisables."""
    def __init__(self, workspace):
        self.workspace=Path(workspace).resolve()
        self.path=self.workspace/".berkios"/"corrections.json"
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.items=self._load()

    def _load(self):
        if self.path.exists():
            try: return json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError: return []
        return []

    def _save(self):
        self.path.write_text(json.dumps(self.items,indent=2,ensure_ascii=False),encoding="utf-8")

    def _git(self,args):
        try:
            r=subprocess.run(["git",*args],cwd=self.workspace,shell=False,
                             capture_output=True,text=True,timeout=10)
            return r.stdout.strip() if r.returncode==0 else ""
        except Exception:
            return ""

    def capture_git(self):
        return {
            "commit": self._git(["rev-parse","HEAD"]),
            "branch": self._git(["branch","--show-current"]),
        }

    def remember(self, error, diagnosis=None, proposal=None, verification=None,
                 run_id=None, files=None, git=None):
        git=git or self.capture_git()
        item={
            "id":f"corr-{len(self.items)+1}",
            "created_at":datetime.now(timezone.utc).isoformat(),
            "status":"corrected",
            "error":{
                "id":error.id,"kind":error.kind.value,"message":error.message,
                "file":error.file,"line":error.line,"code":error.code
            },
            "diagnosis":diagnosis or {},
            "files":files or ([error.file] if error.file else []),
            "proposal":proposal or {},
            "verification":verification or {},
            "run_id":run_id,
            "git":git,
        }
        self.items.append(item); self._save()
        return item

    def search(self, error, limit=5):
        terms=set(re.findall(r"[a-zA-Z_][a-zA-Z0-9_]{3,}",error.message.lower()))
        ranked=[]
        for item in self.items:
            e=item.get("error",{})
            hay=(e.get("message","")+" "+str(item.get("diagnosis",""))).lower()
            score=sum(1 for t in terms if t in hay)
            if e.get("kind")==error.kind.value: score+=3
            if error.file and e.get("file")==error.file: score+=4
            if score: ranked.append((score,item))
        ranked.sort(key=lambda x:(x[0],x[1].get("created_at","")),reverse=True)
        return [x[1] for x in ranked[:limit]]

    def list(self,limit=100):
        return self.items[-limit:]

    def recall(self,error,limit=3):
        matches=self.search(error,limit)
        return {
            "query":{"kind":error.kind.value,"message":error.message,"file":error.file},
            "matches":matches,
            "hint": ("Une correction historique similaire existe."
                     if matches else "Aucune correction historique similaire trouvée.")
        }


# Berkios 4.0 compatibility helpers

def _b40_remember(
    self,
    *,
    error_id=None,
    diagnosis=None,
    files=None,
    proposal=None,
    verification=None,
    run_id=None,
    git_commit=None,
    git_branch=None,
    correction_id=None,
    message="",
    symbols=None,
    created_at=None,
):
    record = {
        "correction_id": correction_id,
        "error_id": error_id,
        "message": message,
        "diagnosis": diagnosis or {},
        "files": list(files or []),
        "symbols": list(symbols or []),
        "proposal": proposal or {},
        "verification": verification or {},
        "run_id": run_id,
        "git_commit": git_commit,
        "git_branch": git_branch,
        "created_at": created_at,
    }
    path = Path(self.workspace) / ".berkios" / "corrections.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    except Exception:
        data = []
    if not isinstance(data, list):
        data = []
    data.append(record)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return record

def _b40_search(self, *, message="", files=None, symbols=None, limit=5):
    path = Path(self.workspace) / ".berkios" / "corrections.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(data, list):
        return []
    terms = set(re.findall(r"[\w.-]+", str(message).lower()))
    wanted_files = set(files or [])
    wanted_symbols = set(symbols or [])
    scored = []
    for item in data:
        hay = json.dumps(item, ensure_ascii=False).lower()
        score = sum(1 for t in terms if t in hay)
        score += 3 * sum(1 for f in wanted_files if f in item.get("files", []))
        score += 3 * sum(1 for s in wanted_symbols if s in item.get("symbols", []))
        scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for score, item in scored[:limit] if score > 0] or [item for _, item in scored[:limit]]

try:
    CorrectionMemory.remember_v4 = _b40_remember
    CorrectionMemory.search_v4 = _b40_search
except NameError:
    pass
