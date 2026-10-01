from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from threading import RLock
from datetime import datetime, timezone
import json, uuid
from .models import ManagerState, ManagedTrainingRun

class CodixTrainingManager:
    def __init__(self, root=".berkios/training_manager", max_workers=1):
        self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True)
        self._lock=RLock(); self._executor=ThreadPoolExecutor(max_workers=max_workers)
        self._runs={}; self._versions={}; self._load()

    def _load(self):
        for p in self.root.glob("run_*.json"):
            try:
                d=json.loads(p.read_text(encoding="utf-8"))
                d["state"]=ManagerState(d["state"])
                self._runs[d["run_id"]]=ManagedTrainingRun(**d)
            except Exception: pass
        p=self.root/"current.json"
        if p.exists():
            try: self._versions=json.loads(p.read_text(encoding="utf-8"))
            except Exception: pass

    def _save(self, run):
        run.updated_at=datetime.now(timezone.utc).isoformat()
        (self.root/f"run_{run.run_id}.json").write_text(
            json.dumps(run.__dict__,default=lambda x:x.value if hasattr(x,"value") else x,
                       ensure_ascii=False,indent=2),encoding="utf-8")

    def create(self, *, dataset_id, dataset_version, base_version=None):
        run=ManagedTrainingRun(uuid.uuid4().hex[:20],dataset_id,dataset_version,base_version)
        with self._lock: self._runs[run.run_id]=run; self._save(run)
        return run

    def get(self, run_id): return self._runs.get(run_id)

    def start_background(self, run_id, worker):
        run=self.get(run_id)
        if not run: raise KeyError(run_id)
        with self._lock:
            run.state=ManagerState.COLLECTING; run.progress=.05; self._save(run)
        return self._executor.submit(self._execute,run_id,worker)

    def _execute(self, run_id, worker):
        try:
            result=worker(self.get(run_id),self._progress)
            with self._lock:
                run=self.get(run_id)
                if run.state==ManagerState.CANCELLED: return run
                run.metrics.update(result.get("metrics",{})); run.current_version=result.get("version")
                run.progress=1.0
                run.state=ManagerState.READY_TO_PROMOTE if result.get("validated") else ManagerState.REJECTED
                self._save(run)
                return run
        except Exception as e:
            with self._lock:
                run=self.get(run_id); run.state=ManagerState.FAILED; run.error=str(e); self._save(run)
                return run

    def _progress(self, run_id, progress, state=None, metrics=None):
        with self._lock:
            run=self.get(run_id)
            if not run: return
            run.progress=max(0,min(1,float(progress)))
            if state: run.state=ManagerState(state.lower())
            if metrics: run.metrics.update(metrics)
            self._save(run)

    def cancel(self, run_id):
        with self._lock:
            run=self.get(run_id)
            if not run: raise KeyError(run_id)
            if run.state not in (ManagerState.PROMOTED,ManagerState.REJECTED):
                run.state=ManagerState.CANCELLED; self._save(run)
            return run

    def promote(self, run_id, *, version, artifact, score, metadata=None):
        with self._lock:
            run=self.get(run_id)
            if not run or run.state!=ManagerState.READY_TO_PROMOTE:
                raise ValueError("Only a validated run can be promoted.")
            self._versions[version]={"version":version,"artifact":artifact,"score":float(score),"metadata":metadata or {}}
            (self.root/"current.json").write_text(json.dumps(self._versions,indent=2),encoding="utf-8")
            run.state=ManagerState.PROMOTED; run.current_version=version; self._save(run)
            return run

    def versions(self): return dict(self._versions)
