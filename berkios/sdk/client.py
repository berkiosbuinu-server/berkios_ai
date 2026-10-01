import json
from urllib.request import Request, urlopen

class BerkiosClient:
    def __init__(self, base_url="http://127.0.0.1:8765"):
        self.base_url = base_url.rstrip("/")

    def _request(self, method, path, payload=None):
        data = None if payload is None else json.dumps(payload).encode()
        req = Request(self.base_url + path, data=data, method=method,
                      headers={"Content-Type":"application/json"})
        with urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())

    def health(self): return self._request("GET", "/v1/health")
    def tools(self): return self._request("GET", "/v1/tools")
    def providers(self): return self._request("GET", "/v1/providers")
    def context(self): return self._request("GET", "/v1/context")
    def changes(self): return self._request("GET", "/v1/changes")
    def errors(self): return self._request("GET", "/v1/errors")
    def error_history(self): return self._request("GET", "/v1/error-history")
    def corrections(self): return self._request("GET", "/v1/corrections")
    def semantic_memory(self): return self._request("GET", "/v1/memory/semantic")
    def project_relations(self): return self._request("GET", "/v1/project/relations")
    def diagnosis(self, error_id): return self._request("GET", f"/v1/errors/{error_id}/diagnosis")
    def code_analysis(self, error_id): return self._request("GET", f"/v1/errors/{error_id}/code")
    def code_index(self): return self._request("GET", "/v1/code/index")
    def update_context(self, **data): return self._request("POST", "/v1/context", data)
    def run(self, request, **kwargs):
        return self._request("POST", "/v1/runs", {"request": request, **kwargs})
    def run_status(self, run_id):
        return self._request("GET", f"/v1/runs/{run_id}")
    def approve(self, run_id):
        return self._request("POST", f"/v1/runs/{run_id}/approve", {})
    def deny(self, run_id):
        return self._request("POST", f"/v1/runs/{run_id}/deny", {})


def project_graph(self):
    return self.request("GET", "/v1/graph")

def graph_related(self, node_id: str):
    return self.request("GET", "/v1/graph/related/" + node_id)


def graph_impact(self, node_id: str, depth: int = 2):
    return self.request("GET", "/v1/graph/impact/" + node_id + "?depth=" + str(depth))

def graph_context(self, node_id: str, depth: int = 2):
    return self.request("GET", "/v1/graph/context/" + node_id + "?depth=" + str(depth))


def impact_plan(self, request: str, targets: list[str]):
    return self.request("POST", "/v1/agent/impact-plan", {
        "request": request,
        "targets": targets,
    })


def intelligence_snapshot(self, request: str, active_file=None,
                          selection=None, target_nodes=None):
    return self.request("POST", "/v1/intelligence/snapshot", {
        "request": request,
        "active_file": active_file,
        "selection": selection,
        "target_nodes": target_nodes or [],
    })


def prepare_run(self, request: str, active_file=None,
                selection=None, target_nodes=None):
    return self.request("POST", "/v1/runs/prepare", {
        "request": request,
        "active_file": active_file,
        "selection": selection,
        "target_nodes": target_nodes or [],
    })


def start_runtime_run(self, request: str, active_file=None,
                      selection=None, target_nodes=None):
    return self.request("POST", "/v1/runtime/runs", {
        "request": request,
        "active_file": active_file,
        "selection": selection,
        "target_nodes": target_nodes or [],
    })

def runtime_transition(self, run_id: str, state: str, detail=None):
    return self.request("POST", "/v1/runtime/runs/" + run_id + "/transition", {
        "state": state,
        "detail": detail or {},
    })

def runtime_complete(self, run_id: str, result=None):
    return self.request("POST", "/v1/runtime/runs/" + run_id + "/complete", {
        "result": result or {},
    })


def propose_change(self, run_id: str, proposal: dict):
    return self.request("POST", "/v1/runtime/runs/" + run_id + "/proposal", {
        "proposal": proposal,
    })

def request_permission(self, run_id: str, action: str, scope: str):
    return self.request("POST", "/v1/runtime/runs/" + run_id + "/permission", {
        "action": action,
        "scope": scope,
    })

def approve_runtime(self, run_id: str, action: str, scope: str):
    return self.request("POST", "/v1/runtime/runs/" + run_id + "/approve", {
        "action": action,
        "scope": scope,
    })

def verify_runtime(self, run_id: str, result: dict):
    return self.request("POST", "/v1/runtime/runs/" + run_id + "/verify", {
        "result": result,
    })


def cycle_propose(self, run_id: str, proposal: dict):
    return self.request("POST", "/v1/cycle/" + run_id + "/propose", {
        "proposal": proposal,
    })

def cycle_apply(self, run_id: str, proposal: dict):
    return self.request("POST", "/v1/cycle/" + run_id + "/apply", {
        "proposal": proposal,
    })

def cycle_verify(self, run_id: str, target=None):
    return self.request("POST", "/v1/cycle/" + run_id + "/verify", {
        "target": target,
    })

def cycle_repair(self, run_id: str, failure: dict):
    return self.request("POST", "/v1/cycle/" + run_id + "/repair", {
        "failure": failure,
    })


def provider_decide(self, request: str, context: dict):
    return self.request("POST", "/v1/provider/decide", {
        "request": request,
        "context": context,
    })

def provider_propose(self, run_id: str, request: str, context: dict):
    return self.request("POST", "/v1/provider/propose", {
        "run_id": run_id,
        "request": request,
        "context": context,
    })

def provider_repair(self, run_id: str, request: str,
                    context: dict, failure: dict):
    return self.request("POST", "/v1/provider/repair", {
        "run_id": run_id,
        "request": request,
        "context": context,
        "failure": failure,
    })


def provider_context(self, request: str, active_file=None,
                     selection=None, target_nodes=None):
    return self.request("POST", "/v1/provider/context", {
        "request": request,
        "active_file": active_file,
        "selection": selection,
        "target_nodes": target_nodes or [],
    })

def context_aware_decide(self, request: str, active_file=None,
                         selection=None, target_nodes=None):
    return self.request("POST", "/v1/provider/context-decide", {
        "request": request,
        "active_file": active_file,
        "selection": selection,
        "target_nodes": target_nodes or [],
    })


def loop_analyze(self, run_id: str, request: str, **context):
    return self.request("POST", "/v1/loop/" + run_id + "/analyze", {
        "request": request,
        **context,
    })

def loop_propose(self, run_id: str, request: str, **context):
    return self.request("POST", "/v1/loop/" + run_id + "/propose", {
        "request": request,
        **context,
    })

def loop_repair(self, run_id: str, request: str,
                failure: dict, **context):
    return self.request("POST", "/v1/loop/" + run_id + "/repair", {
        "request": request,
        "failure": failure,
        **context,
    })


def loop2_run(self, run_id: str, request: str, **context):
    return self.request("POST", "/v1/loop2/" + run_id + "/run", {
        "request": request,
        **context,
    })

def loop2_apply(self, run_id: str, proposal: dict):
    return self.request("POST", "/v1/loop2/" + run_id + "/apply", {
        "proposal": proposal,
    })

def loop2_verify(self, run_id: str, target=None):
    return self.request("POST", "/v1/loop2/" + run_id + "/verify", {
        "target": target,
    })

def loop2_continue(self, run_id: str, request: str,
                   verification: dict, **context):
    return self.request("POST", "/v1/loop2/" + run_id + "/continue", {
        "request": request,
        "verification": verification,
        **context,
    })


def repair_context(self, run_id: str, request: str,
                   failure: dict, **context):
    return self.request("POST", "/v1/repair/context/" + run_id, {
        "request": request,
        "failure": failure,
        **context,
    })

def repair_decide(self, run_id: str, request: str,
                  failure: dict, **context):
    return self.request("POST", "/v1/repair/decide/" + run_id, {
        "request": request,
        "failure": failure,
        **context,
    })


# Berkios 4.0 — self-learning correction helpers
def capture_correction(self, payload):
    return self.request("POST", "/v1/corrections/capture", payload)

def relevant_corrections(self, params=None):
    return self.request("GET", "/v1/corrections/relevant", params or {})


# Berkios 5.2 — provider decision integration
def provider_decision(self, request: str, context: dict):
    return self._request("POST", "/v1/provider/decision", {
        "request": request,
        "context": context,
    })


def select_provider(self, provider: str):
    return self._request("POST", "/v1/provider/select", {"provider": provider})

BerkiosClient.provider_decision = provider_decision
BerkiosClient.select_provider = select_provider
