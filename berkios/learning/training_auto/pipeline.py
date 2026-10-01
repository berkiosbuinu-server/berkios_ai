from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Callable, Iterable, Any
from .models import AutoTrainingConfig, AutoTrainingRun, TrainingStatus

class AutoTrainingPipeline:
    """Controlled automatic training orchestrator.

    The default backend is an adapter: it prepares a training manifest and
    delegates actual weight updates to a registered trainer. It never silently
    uploads private project data or promotes a worse model.
    """
    def __init__(self, root=".berkios/auto_training", config=None):
        self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True)
        self.config=config or AutoTrainingConfig()
        self.trainer: Callable[[Path, Path, AutoTrainingConfig], dict[str,Any]]|None=None

    def register_trainer(self, trainer):
        self.trainer=trainer

    def _id(self, dataset_id, version):
        return hashlib.sha256(f"{dataset_id}:{version}".encode()).hexdigest()[:20]

    def start(self, *, dataset_id, dataset_version, base_model, examples,
              consent=True, human_approved=False, baseline_score=0.0):
        run=AutoTrainingRun(
            run_id=self._id(dataset_id,dataset_version),
            dataset_id=dataset_id, dataset_version=dataset_version,
            base_model=base_model, config=self.config.__dict__.copy(),
            metrics={"baseline_score": float(baseline_score)}
        )
        if self.config.require_consent and not consent:
            run.status=TrainingStatus.REJECTED; run.reason="Explicit learning consent is required."
            return self._save(run)
        if self.config.require_human_approval and not human_approved:
            run.status=TrainingStatus.REJECTED; run.reason="Human approval is required for automatic training."
            return self._save(run)

        run.status=TrainingStatus.EVALUATING
        items=list(examples)
        scores=[float(x.get("quality_score",1.0)) for x in items]
        avg=sum(scores)/len(scores) if scores else 0.0
        run.metrics["dataset_quality"]=avg
        run.metrics["examples"]=float(len(items))
        if avg < self.config.min_quality_score:
            run.status=TrainingStatus.REJECTED; run.reason="Dataset quality below training threshold."
            return self._save(run)

        run.status=TrainingStatus.PREPARING
        manifest=self.root/f"{run.run_id}.train.jsonl"
        with manifest.open("w",encoding="utf-8") as f:
            for x in items:
                f.write(json.dumps(x,ensure_ascii=False)+"\n")

        run.status=TrainingStatus.TRAINING
        if self.trainer is None:
            run.status=TrainingStatus.REJECTED
            run.reason="No training backend registered; manifest prepared but weights were not changed."
            run.artifact=str(manifest)
            return self._save(run)

        try:
            result=self.trainer(manifest, self.root, self.config)
            run.artifact=result.get("artifact")
            run.metrics.update({k:float(v) for k,v in result.get("metrics",{}).items()})
            run.status=TrainingStatus.VALIDATING
            validation=float(run.metrics.get("validation_score",0.0))
            if validation < self.config.min_validation_score:
                run.status=TrainingStatus.REJECTED
                run.reason="Validation score below promotion threshold."
            elif validation < float(baseline_score)-self.config.max_quality_drop:
                run.status=TrainingStatus.REJECTED
                run.reason="New model regressed beyond allowed quality drop."
            elif self.config.auto_promote:
                run.status=TrainingStatus.PROMOTED
            else:
                run.reason="Training passed validation; promotion requires explicit promotion step."
        except Exception as exc:
            run.status=TrainingStatus.FAILED
            run.reason=str(exc)
        return self._save(run)

    def promote(self, run: AutoTrainingRun):
        if run.status != TrainingStatus.VALIDATING:
            raise ValueError("Only a validated run can be promoted.")
        run.status=TrainingStatus.PROMOTED
        run.updated_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()
        return self._save(run)

    def _save(self, run):
        path=self.root/f"{run.run_id}.json"
        path.write_text(json.dumps(run.__dict__,default=lambda x:x.value if hasattr(x,"value") else x,
                                   ensure_ascii=False,indent=2),encoding="utf-8")
        return run
