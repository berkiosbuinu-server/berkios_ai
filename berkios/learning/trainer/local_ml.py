from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import importlib.util
import json

@dataclass
class LocalMLAvailability:
    torch: bool
    transformers: bool
    peft: bool
    accelerate: bool
    bitsandbytes: bool

    @property
    def lora_ready(self) -> bool:
        return self.torch and self.transformers and self.peft

def detect_local_ml() -> LocalMLAvailability:
    def has(name: str) -> bool:
        return importlib.util.find_spec(name) is not None
    return LocalMLAvailability(
        torch=has("torch"),
        transformers=has("transformers"),
        peft=has("peft"),
        accelerate=has("accelerate"),
        bitsandbytes=has("bitsandbytes"),
    )

class LocalMLBackend:
    """Optional real local LoRA backend.

    The backend is imported lazily so Berkios itself does not require a heavy
    ML stack just to start. It raises a clear error when dependencies are absent.

    Actual model training is delegated to Transformers/PEFT and requires the
    caller to provide a local model identifier/path and a compatible dataset.
    """

    def __init__(self, model_name_or_path: str, output_dir: str | Path):
        self.model_name_or_path=model_name_or_path
        self.output_dir=Path(output_dir)
        self.output_dir.mkdir(parents=True,exist_ok=True)

    def train_batch(self, batch, state, config):
        raise RuntimeError(
            "LocalMLBackend requires the full Transformers/PEFT training adapter. "
            "Use train_dataset() for the real local LoRA path."
        )

    def train_dataset(
        self,
        records: list[dict[str, Any]],
        *,
        config,
        lora_r: int = 16,
        lora_alpha: int = 32,
        lora_dropout: float = 0.05,
        target_modules: list[str] | None = None,
    ) -> dict[str, Any]:
        availability=detect_local_ml()
        if not availability.lora_ready:
            missing=[
                name for name, ok in {
                    "torch": availability.torch,
                    "transformers": availability.transformers,
                    "peft": availability.peft,
                }.items() if not ok
            ]
            raise RuntimeError(
                "Real local LoRA training is unavailable. Missing: " + ", ".join(missing)
            )

        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
        from peft import LoraConfig, get_peft_model, TaskType

        # Keep dataset creation local and explicit.
        tokenizer=AutoTokenizer.from_pretrained(self.model_name_or_path, local_files_only=True)
        model=AutoModelForCausalLM.from_pretrained(self.model_name_or_path, local_files_only=True)

        if tokenizer.pad_token is None:
            tokenizer.pad_token=tokenizer.eos_token

        lora=LoraConfig(
            r=lora_r,
            lora_alpha=lora_alpha,
            lora_dropout=lora_dropout,
            bias="none",
            task_type=TaskType.CAUSAL_LM,
            target_modules=target_modules,
        )
        model=get_peft_model(model,lora)

        class _Dataset(torch.utils.data.Dataset):
            def __init__(self, rows):
                self.rows=rows
            def __len__(self):
                return len(self.rows)
            def __getitem__(self, i):
                text=self.rows[i]["input"] + "\n" + self.rows[i]["target"]
                enc=tokenizer(
                    text,
                    truncation=True,
                    max_length=1024,
                    padding="max_length",
                )
                enc["labels"]=enc["input_ids"].copy()
                return {k: torch.tensor(v) for k,v in enc.items()}

        dataset=_Dataset(records)
        args=TrainingArguments(
            output_dir=str(self.output_dir),
            num_train_epochs=config.epochs,
            per_device_train_batch_size=config.batch_size,
            learning_rate=config.learning_rate,
            save_strategy="steps",
            save_steps=max(1,config.checkpoint_every_steps),
            logging_steps=1,
            report_to=[],
            seed=config.seed,
        )
        trainer=Trainer(model=model,args=args,train_dataset=dataset)
        result=trainer.train()
        trainer.save_model(str(self.output_dir/"final_adapter"))
        tokenizer.save_pretrained(str(self.output_dir/"final_adapter"))
        return {
            "artifact": str(self.output_dir/"final_adapter"),
            "metrics": {
                "train_loss": float(getattr(result,"training_loss",0.0)),
            },
            "backend": "transformers-peft-local",
        }

def environment_report() -> dict[str, Any]:
    a=detect_local_ml()
    return {
        "torch": a.torch,
        "transformers": a.transformers,
        "peft": a.peft,
        "accelerate": a.accelerate,
        "bitsandbytes": a.bitsandbytes,
        "lora_ready": a.lora_ready,
    }
