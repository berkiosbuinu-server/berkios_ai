from pathlib import Path
from datetime import datetime, timezone
import json, re

class SemanticMemory:
    """Mémoire locale des connaissances structurelles du projet."""
    CATEGORIES={"architecture","convention","decision","dependency","relation","correction","note"}

    def __init__(self, workspace):
        self.workspace=Path(workspace).resolve()
        self.path=self.workspace/".berkios"/"semantic_memory.json"
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.items=self._load()

    def _load(self):
        if self.path.exists():
            try:return json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:return []
        return []

    def _save(self):
        self.path.write_text(json.dumps(self.items,indent=2,ensure_ascii=False),encoding="utf-8")

    def remember(self, category, content, source="agent", tags=None,
                 files=None, related=None):
        if category not in self.CATEGORIES: raise ValueError(f"Unknown category: {category}")
        item={
            "id":f"sem-{len(self.items)+1}",
            "category":category,
            "content":content,
            "source":source,
            "tags":tags or [],
            "files":files or [],
            "related":related or [],
            "created_at":datetime.now(timezone.utc).isoformat()
        }
        self.items.append(item); self._save()
        return item

    def list(self, category=None, limit=100):
        data=[x for x in self.items if category is None or x["category"]==category]
        return data[-limit:]

    def search(self, query, files=None, limit=10):
        terms=set(re.findall(r"[a-zA-Z_][a-zA-Z0-9-]{2,}",query.lower()))
        ranked=[]
        for item in self.items:
            hay=(item["content"]+" "+" ".join(item["tags"])+" "+item["category"]).lower()
            score=sum(1 for t in terms if t in hay)
            if files:
                score += 3*sum(1 for f in files if f in item.get("files",[]))
            if score: ranked.append((score,item))
        ranked.sort(key=lambda x:(x[0],x[1]["created_at"]),reverse=True)
        return [x[1] for x in ranked[:limit]]

    def context(self, query, files=None, limit=5):
        matches=self.search(query,files,limit)
        return {
            "query":query,
            "knowledge":matches,
            "summary":("Connaissances projet pertinentes trouvées."
                       if matches else "Aucune connaissance sémantique pertinente.")
        }
