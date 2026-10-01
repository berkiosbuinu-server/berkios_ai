from ..sdk.client import BerkiosClient

class IBookBridge:
    def __init__(self, base_url="http://127.0.0.1:8765"):
        self.client = BerkiosClient(base_url)

    def sync_editor(self, **context):
        return self.client.update_context(**context)

    def ask(self, request, **kwargs):
        return self.client.run(request, **kwargs)

    def approve(self, run_id):
        return self.client.approve(run_id)

    def deny(self, run_id):
        return self.client.deny(run_id)

    def run_status(self, run_id):
        return self.client.run_status(run_id)

    def pending_changes(self):
        return self.client.changes()

    def errors(self):
        return self.client.errors()

    def diagnose_error(self, error_id):
        return self.client.diagnosis(error_id)

    def analyze_error_code(self, error_id):
        return self.client.code_analysis(error_id)

    def code_index(self):
        return self.client.code_index()

    def error_history(self):
        return self.client.error_history()

    def corrections(self):
        return self.client.corrections()

    def semantic_memory(self):
        return self.client.semantic_memory()

    def project_relations(self):
        return self.client.project_relations()


def impact_plan(self, request: str, targets: list[str]):
    return self.client.impact_plan(request, targets)


def intelligence_snapshot(self, request: str, active_file=None,
                          selection=None, target_nodes=None):
    return self.client.intelligence_snapshot(
        request, active_file, selection, target_nodes
    )


def prepare_run(self, request: str, active_file=None,
                selection=None, target_nodes=None):
    return self.client.prepare_run(
        request, active_file, selection, target_nodes
    )


def start_runtime_run(self, request: str, active_file=None,
                      selection=None, target_nodes=None):
    return self.client.start_runtime_run(
        request, active_file, selection, target_nodes
    )

def runtime_transition(self, run_id: str, state: str, detail=None):
    return self.client.runtime_transition(run_id, state, detail)

def runtime_complete(self, run_id: str, result=None):
    return self.client.runtime_complete(run_id, result)


def propose_change(self, run_id: str, proposal: dict):
    return self.client.propose_change(run_id, proposal)

def request_permission(self, run_id: str, action: str, scope: str):
    return self.client.request_permission(run_id, action, scope)

def approve_runtime(self, run_id: str, action: str, scope: str):
    return self.client.approve_runtime(run_id, action, scope)

def verify_runtime(self, run_id: str, result: dict):
    return self.client.verify_runtime(run_id, result)


def cycle_propose(self, run_id: str, proposal: dict):
    return self.client.cycle_propose(run_id, proposal)

def cycle_apply(self, run_id: str, proposal: dict):
    return self.client.cycle_apply(run_id, proposal)

def cycle_verify(self, run_id: str, target=None):
    return self.client.cycle_verify(run_id, target)

def cycle_repair(self, run_id: str, failure: dict):
    return self.client.cycle_repair(run_id, failure)


def provider_decide(self, request: str, context: dict):
    return self.client.provider_decide(request, context)

def provider_propose(self, run_id: str, request: str, context: dict):
    return self.client.provider_propose(run_id, request, context)

def provider_repair(self, run_id: str, request: str,
                    context: dict, failure: dict):
    return self.client.provider_repair(
        run_id, request, context, failure
    )


def provider_context(self, request: str, active_file=None,
                     selection=None, target_nodes=None):
    return self.client.provider_context(
        request, active_file, selection, target_nodes
    )

def context_aware_decide(self, request: str, active_file=None,
                         selection=None, target_nodes=None):
    return self.client.context_aware_decide(
        request, active_file, selection, target_nodes
    )


def loop_analyze(self, run_id: str, request: str, **context):
    return self.client.loop_analyze(run_id, request, **context)

def loop_propose(self, run_id: str, request: str, **context):
    return self.client.loop_propose(run_id, request, **context)

def loop_repair(self, run_id: str, request: str,
                failure: dict, **context):
    return self.client.loop_repair(
        run_id, request, failure, **context
    )


def loop2_run(self, run_id: str, request: str, **context):
    return self.client.loop2_run(run_id, request, **context)

def loop2_apply(self, run_id: str, proposal: dict):
    return self.client.loop2_apply(run_id, proposal)

def loop2_verify(self, run_id: str, target=None):
    return self.client.loop2_verify(run_id, target)

def loop2_continue(self, run_id: str, request: str,
                   verification: dict, **context):
    return self.client.loop2_continue(
        run_id, request, verification, **context
    )


def repair_context(self, run_id: str, request: str,
                   failure: dict, **context):
    return self.client.repair_context(
        run_id, request, failure, **context
    )

def repair_decide(self, run_id: str, request: str,
                  failure: dict, **context):
    return self.client.repair_decide(
        run_id, request, failure, **context
    )


# Berkios 4.0 — self-learning correction helpers
def capture_correction(self, payload):
    return self.request("POST", "/v1/corrections/capture", payload)

def relevant_corrections(self, params=None):
    return self.request("GET", "/v1/corrections/relevant", params or {})
