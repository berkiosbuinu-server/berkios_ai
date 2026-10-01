from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
import json
from .models import TrainerConfig, TrainerCheckpoint, TrainerResult, TrainerStatus

class TrainerBackend(ABC):
    """Backend contract for a real local or remote trainer."""

    @abstractmethod
    def train_batch(self, batch, state, config: TrainerConfig) -> dict:
        """Train one batch and return metrics/state updates."""
        raise NotImplementedError

    def save_artifact(self, output_dir: Path, state: dict, step: int) -> str:
        path=output_dir/f"checkpoint-{step}.json"
        path.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
        return str(path)

class CodixTrainerEngine:
    """Checkpointed training engine; model-specific math lives in the backend."""

    def __init__(self, root=".berkios/trainer_runs"):
        self.root=Path(root)
        self.root.mkdir(parents=True,exist_ok=True)

    def train(self, *, run_id, examples, backend: TrainerBackend,
              config: TrainerConfig, resume_from: str | None=None) -> TrainerResult:
        out=Path(config.output_dir)/run_id
        out.mkdir(parents=True,exist_ok=True)
        items=list(examples)
        if not items:
            return TrainerResult(run_id,TrainerStatus.FAILED,0,0,reason="Empty training dataset.")

        state={"step":0,"epoch":0}
        if resume_from:
            rp=Path(resume_from)
            if rp.exists():
                state=json.loads(rp.read_text(encoding="utf-8"))

        step=int(state.get("step",0))
        start_epoch=int(state.get("epoch",0))
        last_metrics={}
        max_steps=config.max_steps

        try:
            for epoch in range(start_epoch, max(0,config.epochs)):
                for i in range(0,len(items),max(1,config.batch_size)):
                    if max_steps is not None and step >= max_steps:
                        return self._finish(run_id,step,epoch,out,last_metrics,backend,state,TrainerStatus.COMPLETED)

                    batch=items[i:i+max(1,config.batch_size)]
                    update=backend.train_batch(batch,state,config) or {}
                    state.update(update.get("state",{}))
                    step+=1
                    state["step"]=step
                    state["epoch"]=epoch
                    last_metrics={k:float(v) for k,v in update.get("metrics",{}).items()}

                    if step % max(1,config.checkpoint_every_steps)==0:
                        artifact=backend.save_artifact(out,state,step)
                        cp=TrainerCheckpoint(run_id,step,epoch,artifact,last_metrics)
                        self._save_checkpoint(cp)

                state["epoch"]=epoch+1

            return self._finish(run_id,step,config.epochs,out,last_metrics,backend,state,TrainerStatus.COMPLETED)
        except KeyboardInterrupt:
            return self._finish(run_id,step,start_epoch,out,last_metrics,backend,state,TrainerStatus.CANCELLED)
        except Exception as exc:
            return TrainerResult(run_id,TrainerStatus.FAILED,step,start_epoch,metrics=last_metrics,reason=str(exc))

    def _finish(self,run_id,step,epochs,out,metrics,backend,state,status):
        artifact=backend.save_artifact(out,state,step)
        result=TrainerResult(run_id,status,step,epochs,artifact=artifact,metrics=metrics)
        (self.root/f"{run_id}.result.json").write_text(
            json.dumps(result.__dict__,default=lambda x:x.value if hasattr(x,"value") else x,
                       ensure_ascii=False,indent=2),encoding="utf-8")
        return result

    def _save_checkpoint(self, cp: TrainerCheckpoint):
        p=self.root/f"{cp.run_id}.checkpoint.json"
        p.write_text(json.dumps(cp.__dict__,ensure_ascii=False,indent=2),encoding="utf-8")
