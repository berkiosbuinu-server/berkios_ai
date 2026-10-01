from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import json, uuid

from .models import LoopConfig, LoopState, ContinuousRun

class CodixContinuousLearningLoop:
    """Coordinates collection -> dataset -> training -> evaluation -> promotion.

    Each stage is injected as a callable so Berkios stays provider/model neutral.
    """

    def __init__(self, root=".berkios/continuous_learning", config=None):
        self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True)
        self.config=config or LoopConfig()
        self.runs={}

    def _save(self, run):
        run.updated_at=datetime.now(timezone.utc).isoformat()
        (self.root/f"run_{run.run_id}.json").write_text(
            json.dumps(run.__dict__,default=lambda x:x.value if hasattr(x,"value") else x,
                       ensure_ascii=False,indent=2),encoding="utf-8")

    def run_once(self, *, collect, build_dataset, train, evaluate, promote=None,
                 baseline_score=0.0):
        run=ContinuousRun(uuid.uuid4().hex[:20])
        self.runs[run.run_id]=run
        try:
            run.state=LoopState.COLLECTING; run.progress=.05; self._save(run)
            examples=list(collect())
            run.metrics["new_examples"]=len(examples)
            if len(examples)<self.config.min_new_examples:
                run.state=LoopState.REJECTED
                run.reason="Not enough new approved examples."
                self._save(run); return run

            run.state=LoopState.DATASET; run.progress=.25; self._save(run)
            dataset=build_dataset(examples)

            run.state=LoopState.TRAINING; run.progress=.45; self._save(run)
            trained=train(dataset)

            run.state=LoopState.EVALUATING; run.progress=.70; self._save(run)
            evaluation=evaluate(trained)
            score=float(evaluation.get("score",0.0))
            run.metrics["validation_score"]=score
            run.metrics["baseline_score"]=float(baseline_score)
            delta=score-float(baseline_score)
            run.metrics["delta"]=delta

            if score<self.config.min_validation_score:
                run.state=LoopState.REJECTED
                run.reason="Validation score below threshold."
            elif delta < -self.config.max_regression:
                run.state=LoopState.REJECTED
                run.reason="Regression exceeds allowed limit."
            else:
                run.state=LoopState.PROMOTING
                run.progress=.90; self._save(run)
                run.version=trained.get("version")
                if self.config.auto_promote and promote:
                    promote(trained,evaluation)
                    run.state=LoopState.COMPLETED
                else:
                    run.state=LoopState.COMPLETED
                    run.reason="Validated; promotion remains explicit."
            run.progress=1.0; self._save(run)
            return run
        except Exception as exc:
            run.state=LoopState.FAILED; run.reason=str(exc); run.progress=1.0
            self._save(run); return run
