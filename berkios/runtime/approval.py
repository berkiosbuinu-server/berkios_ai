from __future__ import annotations
from berkios.approval import ApprovalManager, ApprovalExecutionBridge

class RuntimeApprovalCenter:
    def __init__(self, runtime):
        self.runtime = runtime
        self.manager = ApprovalManager(runtime.create_persistence())
        self.bridge = ApprovalExecutionBridge(
            self.manager,
            runtime.create_execution_control().controller,
        )

    def request(self, **kwargs):
        request = self.manager.create(**kwargs)
        self.bridge.bind(request, kwargs.get("metadata", {}).get("step_id"))
        return request

    def bind(self, approval_id, step_id=None):
        request = self.manager.get(approval_id)
        if request is None:
            raise KeyError(approval_id)
        return self.bridge.bind(request, step_id)

    def pending(self):
        return self.manager.pending()

    def get(self, approval_id):
        return self.manager.get(approval_id)

    def approve(self, approval_id):
        return self.bridge.decide(approval_id, True)

    def reject(self, approval_id):
        return self.bridge.decide(approval_id, False)

    def is_approved(self, approval_id):
        return self.bridge.is_approved(approval_id)
