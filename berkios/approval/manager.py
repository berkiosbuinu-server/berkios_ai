from __future__ import annotations
import json
from .models import ApprovalRequest, ApprovalDecision

class ApprovalManager:
    def __init__(self, persistence=None):
        self.persistence = persistence
        self.requests: dict[str, ApprovalRequest] = {}
        self._restore()

    def _restore(self):
        if self.persistence is None:
            return
        try:
            rows = self.persistence.repository.database.SessionLocal()
            # Approval rows are intentionally restored through the repository's
            # database layer to keep the public repository API small.
            from berkios.persistence.models import PersistentApproval
            from sqlalchemy import select
            with rows as db:
                data = db.scalars(select(PersistentApproval)).all()
                for row in data:
                    payload = json.loads(row.payload_json or "{}")
                    try:
                        request = ApprovalRequest(**payload)
                        request.approval_id = row.id
                        request.decision = ApprovalDecision(row.decision)
                        self.requests[request.approval_id] = request
                    except Exception:
                        continue
        except Exception:
            return

    def create(self, **kwargs):
        request = ApprovalRequest(**kwargs)
        self.requests[request.approval_id] = request
        self._persist(request)
        return request

    def get(self, approval_id):
        return self.requests.get(approval_id)

    def pending(self):
        return [
            x for x in self.requests.values()
            if x.decision == ApprovalDecision.PENDING
        ]

    def approve(self, approval_id):
        request = self._require(approval_id)
        result = request.decide(True)
        self._persist(request)
        return result

    def reject(self, approval_id):
        request = self._require(approval_id)
        result = request.decide(False)
        self._persist(request)
        return result

    def _persist(self, request):
        if self.persistence is None:
            return
        try:
            payload = request.to_dict() if hasattr(request, "to_dict") else {
                k: v for k, v in vars(request).items()
                if not k.startswith("_")
            }
            self.persistence.repository.save_approval(
                request.approval_id,
                request.decision.value if hasattr(request.decision, "value") else str(request.decision),
                payload,
                payload.get("run_id") or payload.get("metadata", {}).get("run_id"),
                payload.get("step_id") or payload.get("metadata", {}).get("step_id"),
            )
            self.persistence.record_event(
                "approval.updated",
                {"approval_id": request.approval_id, "decision": str(request.decision)},
                payload.get("run_id") or payload.get("metadata", {}).get("run_id"),
            )
        except Exception:
            pass

    def _require(self, approval_id):
        request = self.get(approval_id)
        if request is None:
            raise KeyError(approval_id)
        return request
