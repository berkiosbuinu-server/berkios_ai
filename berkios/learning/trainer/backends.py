from __future__ import annotations
from pathlib import Path
from .models import TrainerConfig

class SimulatedLocalAdapter:
    """Development adapter proving the checkpoint protocol without claiming ML training.

    Replace this backend with a real LoRA/QLoRA backend when the local ML stack
    (model, tokenizer, tensors, accelerator) is installed.
    """
    def train_batch(self,batch,state,config:TrainerConfig):
        loss=max(0.01,1.0/(1+state.get("step",0)))
        return {"metrics":{"loss":loss},"state":{"last_batch_size":len(batch)}}

    def save_artifact(self,output_dir:Path,state:dict,step:int)->str:
        p=output_dir/f"adapter-checkpoint-{step}.json"
        p.write_text(
            '{"kind":"training-adapter-checkpoint","note":"development adapter; not model weights",'
            '"step":'+str(step)+',"state":'+__import__("json").dumps(state)+'}',
            encoding="utf-8")
        return str(p)
