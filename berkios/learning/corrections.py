from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import json
import uuid
from typing import Any, Iterable

from berkios.memory.corrections import CorrectionMemory


@dataclass
class CorrectionCapture:
    error_id: str | None
    run_id: str | None
    message: str
    diagnosis: dict[str, Any]
    proposal: dict[str, Any]
    verification: dict[str, Any]
    files: list[str]
    symbols: list[str]
    git_commit: str | None
    git_branch: str | None
    created_at: str
    correction_id: str

    @classmethod
    def create(
        cls,
        *,
        message: str,
        diagnosis: dict[str, Any] | None = None,
        proposal: dict[str, Any] | None = None,
        verification: dict[str, Any] | None = None,
        error_id: str | None = None,
        run_id: str | None = None,
        files: Iterable[str] = (),
        symbols: Iterable[str] = (),
        git_commit: str | None = None,
        git_branch: str | None = None,
    ) -> "CorrectionCapture":
        return cls(
            error_id=error_id,
            run_id=run_id,
            message=message,
            diagnosis=diagnosis or {},
            proposal=proposal or {},
            verification=verification or {},
            files=list(files),
            symbols=list(symbols),
            git_commit=git_commit,
            git_branch=git_branch,
            created_at=datetime.now(timezone.utc).isoformat(),
            correction_id=uuid.uuid4().hex,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SelfLearningCorrectionLoop:
    """
    Records only validated corrections.

    A correction becomes reusable knowledge only after the caller confirms
    that verification succeeded. Historical knowledge is contextual and
    never grants permission to apply a future change.
    """

    def __init__(
        self,
        workspace: str | Path,
        correction_memory: CorrectionMemory | None = None,
        event_sink=None,
    ):
        self.workspace = Path(workspace).resolve()
        self.memory = correction_memory or CorrectionMemory(self.workspace)
        self.event_sink = event_sink

    def capture(
        self,
        *,
        message: str,
        diagnosis: dict[str, Any] | None = None,
        proposal: dict[str, Any] | None = None,
        verification: dict[str, Any] | None = None,
        error_id: str | None = None,
        run_id: str | None = None,
        files: Iterable[str] = (),
        symbols: Iterable[str] = (),
        git_commit: str | None = None,
        git_branch: str | None = None,
    ) -> CorrectionCapture:
        verification = verification or {}
        if verification.get("success") is not True:
            raise ValueError(
                "A correction can only be learned after successful verification."
            )

        capture = CorrectionCapture.create(
            message=message,
            diagnosis=diagnosis,
            proposal=proposal,
            verification=verification,
            error_id=error_id,
            run_id=run_id,
            files=files,
            symbols=symbols,
            git_commit=git_commit,
            git_branch=git_branch,
        )

        # Reuse the existing CorrectionMemory contract where possible.
        self.memory.remember(
            error_id=capture.error_id,
            diagnosis=capture.diagnosis,
            files=capture.files,
            proposal=capture.proposal,
            verification=capture.verification,
            run_id=capture.run_id,
            git_commit=capture.git_commit,
            git_branch=capture.git_branch,
            correction_id=capture.correction_id,
            message=capture.message,
            symbols=capture.symbols,
            created_at=capture.created_at,
        )

        if self.event_sink is not None:
            self.event_sink({
                "type": "correction.recorded",
                "correction_id": capture.correction_id,
                "run_id": capture.run_id,
                "error_id": capture.error_id,
                "files": capture.files,
                "symbols": capture.symbols,
            })

        return capture

    def relevant(
        self,
        *,
        message: str = "",
        files: Iterable[str] = (),
        symbols: Iterable[str] = (),
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        return self.memory.search(
            message=message,
            files=list(files),
            symbols=list(symbols),
            limit=limit,
        )
