from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from urllib.parse import urlparse
from ..protocol.schema import health_payload

class Handler(BaseHTTPRequestHandler):
    runtime = None

    def _json(self, code, payload):
        raw = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health": return self._json(200, {"status":"healthy","service":"berkios-api","version":"5.25.0"})
        if path == "/v1": return self._json(200, {"api_version":"v1","runtime":"2.1.0"})
        if path == "/v1/health": return self._json(200, health_payload() | {"runtime_version":"2.1.0"})
        if path == "/v1/tools": return self._json(200, {"tools": self.runtime.tools.list()})
        if path == "/v1/providers":
            details = []
            for name in self.runtime.providers.list():
                provider = self.runtime.providers.providers[name]
                details.append({
                    "name": name,
                    "configured": getattr(provider, "configured", True),
                    "selected": name == self.runtime.providers.selected,
                })
            return self._json(200, {"providers": details, "selected": self.runtime.providers.selected})
        if path == "/v1/persistence/runs":
            try:
                return self._json(200, {
                    "runs": self.runtime.create_persistence().repository.list_runs()
                })
            except Exception as exc:
                return self._json(500, {"error": "persistence_list_failed", "detail": str(exc)})

        if path.startswith("/v1/persistence/events"):
            try:
                cursor = int(body.get("after", 0))
                run_id = body.get("run_id")
                events = self.runtime.create_persistence().repository.events_after(
                    cursor, run_id=run_id
                )
                return self._json(200, {"events": events})
            except Exception as exc:
                return self._json(500, {"error": "persistence_events_failed", "detail": str(exc)})

        if path == "/v1/context": return self._json(200, self.runtime.context.snapshot())
        if path == "/v1/changes": return self._json(200, {"proposals": self.runtime.review.list()})
        if path == "/v1/errors": return self._json(200, {"errors": self.runtime.errors.list()})
        if path == "/v1/error-history": return self._json(200, {"items": self.runtime.error_history.list()})
        if path == "/v1/corrections": return self._json(200, {"items": self.runtime.corrections.list()})
        if path == "/v1/memory/semantic": return self._json(200, {"items": self.runtime.semantic_memory.list()})
        if path == "/v1/project/relations": return self._json(200, self.runtime.project_semantics.summarize())
        if path == "/v1/code/index": return self._json(200, self.runtime.code_index.snapshot())
        if path.startswith("/v1/runs/"):
            run_id = path.split("/")[-1]
            if run_id in self.runtime.runs:
                return self._json(200, self.runtime.runs[run_id].snapshot())
            return self._json(404, {"error":"run_not_found"})
        return self._json(404, {"error":"not_found"})

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length","0"))
        body = json.loads(self.rfile.read(length) or b"{}")

        if path == "/v1/execution/checkpoint":
            try:
                run_id = body.get("run_id")
                plan = body.get("plan", {})
                from berkios.actionplan import ActionPlan, PlannedAction, ActionKind
                actions = [
                    PlannedAction(
                        id=x["id"], kind=ActionKind(x["kind"]),
                        description=x.get("description", ""),
                        capability=x.get("capability"),
                        tool=x.get("tool"), target=x.get("target"),
                        requires_approval=x.get("requires_approval", False),
                        requires_verification=x.get("requires_verification", False),
                        risk=x.get("risk", "low"),
                        depends_on=x.get("depends_on", []),
                        metadata=x.get("metadata", {}),
                    ) for x in plan.get("actions", [])
                ]
                ap = ActionPlan(
                    request=plan.get("request", ""),
                    objective=plan.get("objective", ""),
                    actions=actions,
                    risks=plan.get("risks", []),
                    assumptions=plan.get("assumptions", []),
                    approval_required=plan.get("approval_required", False),
                    verification_required=plan.get("verification_required", True),
                    rationale=plan.get("rationale", ""),
                )
                run = self.runtime.create_execution_control().get(run_id)
                if run is None:
                    return self._json(404, {"error": "run_not_found"})
                checkpoint = self.runtime.create_execution_resumer().checkpoint(
                    run,
                    self.runtime.create_execution_planner().build(
                        ap,
                        self.runtime.create_action_resolver().resolve(ap)
                    ),
                )
                return self._json(200, checkpoint.to_dict())
            except Exception as exc:
                return self._json(400, {"error": "checkpoint_failed", "detail": str(exc)})

        if path == "/v1/codix/profile":
            try:
                return self._json(200, self.runtime.create_codix_learning().codix().to_dict())
            except Exception as exc:
                return self._json(400, {"error":"codix_profile_failed","detail":str(exc)})
        if path == "/v1/codix/learning/consent":
            try:
                x=self.runtime.create_codix_learning()
                c=x.enable_learning(body.get("scope",[])) if body.get("enabled") else x.disable_learning()
                return self._json(200,c.__dict__)
            except Exception as exc:
                return self._json(400,{"error":"learning_consent_failed","detail":str(exc)})
        if path == "/v1/codix/learning/example":
            try:
                x=self.runtime.create_codix_learning()
                e=x.add_example(source=body.get("source","ibook"),provider=body.get("provider"),
                    model=body.get("model"),task=body.get("task",""),
                    input_data=body.get("input_data",{}),output_data=body.get("output_data",{}),
                    feedback=body.get("feedback"),score=body.get("score"),
                    project_hash=body.get("project_hash"))
                return self._json(200,e.to_dict())
            except PermissionError as exc:
                return self._json(403,{"error":"learning_consent_required","detail":str(exc)})
            except Exception as exc:
                return self._json(400,{"error":"learning_example_failed","detail":str(exc)})
        if path == "/v1/codix/learning/dataset":
            try:
                return self._json(200,{"examples":self.runtime.create_codix_learning().dataset()})
            except Exception as exc:
                return self._json(400,{"error":"learning_dataset_failed","detail":str(exc)})
        if path == "/v1/approval/request":
            try:
                center = self.runtime.create_approval_center()
                request = center.request(
                    run_id=body.get("run_id"),
                    action_id=body.get("action_id"),
                    capability=body.get("capability"),
                    title=body.get("title", "Approbation requise"),
                    description=body.get("description", ""),
                    risk=body.get("risk", "medium"),
                    targets=body.get("targets", []),
                    changes=body.get("changes", []),
                    reason=body.get("reason", ""),
                    metadata=body.get("metadata", {}),
                )
                return self._json(200, request.to_dict())
            except Exception as exc:
                return self._json(400, {"error": "approval_request_failed", "detail": str(exc)})

        if path == "/v1/approval/list":
            try:
                center = self.runtime.create_approval_center()
                return self._json(200, {
                    "requests": [x.to_dict() for x in center.pending()]
                })
            except Exception as exc:
                return self._json(400, {"error": "approval_list_failed", "detail": str(exc)})

        if path == "/v1/approval/decide":
            try:
                approval_id = body.get("approval_id")
                if not approval_id:
                    return self._json(400, {"error": "approval_id_required"})
                center = self.runtime.create_approval_center()
                request = (
                    center.approve(approval_id)
                    if body.get("approved") is True
                    else center.reject(approval_id)
                )
                return self._json(200, request.to_dict())
            except KeyError:
                return self._json(404, {"error": "approval_not_found"})
            except Exception as exc:
                return self._json(400, {"error": "approval_decision_failed", "detail": str(exc)})

        if path == "/v1/live/runs":
            try:
                run_id = body.get("run_id")
                if not run_id:
                    return self._json(400, {"error": "run_id_required"})
                bridge = self.runtime.create_live_bridge()
                snapshot = bridge.snapshot(run_id)
                return self._json(200, snapshot.to_dict())
            except KeyError:
                return self._json(404, {"error": "run_not_found"})
            except Exception as exc:
                return self._json(400, {"error": "live_snapshot_failed", "detail": str(exc)})

        if path == "/v1/live/events":
            try:
                run_id = body.get("run_id")
                if not run_id:
                    return self._json(400, {"error": "run_id_required"})
                bridge = self.runtime.create_live_bridge()
                return self._json(200, {
                    "run_id": run_id,
                    "events": bridge.events(run_id, body.get("after", 0)),
                })
            except KeyError:
                return self._json(404, {"error": "run_not_found"})
            except Exception as exc:
                return self._json(400, {"error": "live_events_failed", "detail": str(exc)})

        if path == "/v1/live/pause":
            try:
                run_id = body.get("run_id")
                bridge = self.runtime.create_live_bridge()
                run = bridge.pause(run_id)
                return self._json(200, run.to_dict())
            except KeyError:
                return self._json(404, {"error": "run_not_found"})
            except Exception as exc:
                return self._json(400, {"error": "pause_failed", "detail": str(exc)})

        if path == "/v1/live/cancel":
            try:
                run_id = body.get("run_id")
                bridge = self.runtime.create_live_bridge()
                run = bridge.cancel(run_id)
                return self._json(200, run.to_dict())
            except KeyError:
                return self._json(404, {"error": "run_not_found"})
            except Exception as exc:
                return self._json(400, {"error": "cancel_failed", "detail": str(exc)})

        if path == "/v1/execution/ready":
            try:
                from berkios.actionplan import ActionPlan, PlannedAction, ActionKind
                from berkios.execution import ExecutionPlanner
                pd = body.get("plan", {})
                actions = [
                    PlannedAction(
                        id=x["id"], kind=ActionKind(x["kind"]),
                        description=x.get("description", ""),
                        capability=x.get("capability"),
                        tool=x.get("tool"), target=x.get("target"),
                        requires_approval=x.get("requires_approval", False),
                        requires_verification=x.get("requires_verification", False),
                        risk=x.get("risk", "low"),
                        depends_on=x.get("depends_on", []),
                        metadata=x.get("metadata", {}),
                    ) for x in pd.get("actions", [])
                ]
                plan = ActionPlan(
                    request=pd.get("request", ""),
                    objective=pd.get("objective", ""),
                    actions=actions,
                    risks=pd.get("risks", []),
                    assumptions=pd.get("assumptions", []),
                    approval_required=pd.get("approval_required", False),
                    verification_required=pd.get("verification_required", True),
                    rationale=pd.get("rationale", ""),
                )
                matches = self.runtime.create_action_resolver().resolve(plan)
                execution_plan = self.runtime.create_execution_planner().build(
                    plan, matches
                )
                executor = self.runtime.create_tool_executor()
                results = executor.execute(
                    execution_plan, body.get("context", {})
                )
                return self._json(200, {
                    "plan": execution_plan.to_dict(),
                    "results": [r.to_dict() for r in results],
                })
            except Exception as exc:
                return self._json(400, {
                    "error": "tool_execution_failed",
                    "detail": str(exc),
                })

        if path == "/v1/execution-plan":
            try:
                from berkios.actionplan import ActionPlan, PlannedAction, ActionKind
                from berkios.execution import ExecutionPlanner
                pd = body.get("plan", {})
                actions = [
                    PlannedAction(
                        id=x["id"],
                        kind=ActionKind(x["kind"]),
                        description=x.get("description", ""),
                        capability=x.get("capability"),
                        tool=x.get("tool"),
                        target=x.get("target"),
                        requires_approval=x.get("requires_approval", False),
                        requires_verification=x.get("requires_verification", False),
                        risk=x.get("risk", "low"),
                        depends_on=x.get("depends_on", []),
                        metadata=x.get("metadata", {}),
                    ) for x in pd.get("actions", [])
                ]
                plan = ActionPlan(
                    request=pd.get("request", ""),
                    objective=pd.get("objective", ""),
                    actions=actions,
                    risks=pd.get("risks", []),
                    assumptions=pd.get("assumptions", []),
                    approval_required=pd.get("approval_required", False),
                    verification_required=pd.get("verification_required", True),
                    rationale=pd.get("rationale", ""),
                )
                matches = self.runtime.create_action_resolver().resolve(plan)
                execution = self.runtime.create_execution_planner().build(
                    plan, matches
                )
                return self._json(200, execution.to_dict())
            except Exception as exc:
                return self._json(400, {
                    "error": "execution_plan_failed",
                    "detail": str(exc),
                })

        if path == "/v1/action-plan/resolve":
            plan_data = body.get("plan", {})
            try:
                from berkios.actionplan import ActionPlan, PlannedAction, ActionKind
                actions = []
                for item in plan_data.get("actions", []):
                    actions.append(PlannedAction(
                        id=item["id"],
                        kind=ActionKind(item["kind"]),
                        description=item.get("description", ""),
                        capability=item.get("capability"),
                        tool=item.get("tool"),
                        target=item.get("target"),
                        requires_approval=item.get("requires_approval", False),
                        requires_verification=item.get("requires_verification", False),
                        risk=item.get("risk", "low"),
                        depends_on=item.get("depends_on", []),
                        metadata=item.get("metadata", {}),
                    ))
                plan = ActionPlan(
                    request=plan_data.get("request", ""),
                    objective=plan_data.get("objective", ""),
                    actions=actions,
                    risks=plan_data.get("risks", []),
                    assumptions=plan_data.get("assumptions", []),
                    approval_required=plan_data.get("approval_required", False),
                    verification_required=plan_data.get("verification_required", True),
                    rationale=plan_data.get("rationale", ""),
                )
                resolver = self.runtime.create_action_resolver()
                return self._json(200, {"plan": plan.to_dict(),
                                        "capabilities": resolver.as_dict(plan)})
            except Exception as exc:
                return self._json(400, {
                    "error": "action_plan_resolution_failed",
                    "detail": str(exc),
                })

        if path == "/v1/action-plan":
            decision = body.get("decision", {})
            request = body.get("request", "")
            if not request:
                return self._json(400, {"error": "request_required"})
            try:
                # Reconstruct a lightweight decision object from provider JSON.
                class DecisionPayload:
                    pass
                d = DecisionPayload()
                for key, value in decision.items():
                    setattr(d, key, value)
                planner = self.runtime.create_action_planner()
                plan = planner.plan_from_decision(
                    d, request, body.get("context", {})
                )
                return self._json(200, plan.to_dict())
            except Exception as exc:
                return self._json(400, {
                    "error": "action_plan_failed",
                    "detail": str(exc),
                })

        if path == "/v1/agent/run":
            request = body.get("request", "")
            if not request:
                return self._json(400, {"error": "request_required"})
            try:
                agent = self.runtime.create_provider_agent(
                    max_iterations=body.get("max_iterations", 3)
                )
                result = agent.loop(
                    request,
                    run_id=body.get("run_id"),
                    active_file=body.get("active_file"),
                    selection=body.get("selection"),
                    target_nodes=body.get("target_nodes", []),
                )
                return self._json(200, result.to_dict())
            except Exception as exc:
                return self._json(400, {
                    "error": "agent_run_failed",
                    "detail": str(exc),
                })

        if path == "/v1/provider/decision":
            request = body.get("request", "")
            context = body.get("context", {})
            try:
                decision = self.runtime.decision_integration.decide(
                    self.runtime.providers, request, context
                )
                return self._json(200, decision.to_dict())
            except Exception as exc:
                return self._json(400, {"error": "provider_decision_failed", "detail": str(exc)})

        if path == "/v1/provider/select":
            try:
                self.runtime.providers.select(body.get("provider", ""))
                return self._json(200, {
                    "selected": self.runtime.providers.selected,
                    "providers": self.runtime.providers.list(),
                })
            except Exception as exc:
                return self._json(400, {"error": "provider_select_failed", "detail": str(exc)})

        if path == "/v1/persistence/runs":
            try:
                return self._json(200, {
                    "runs": self.runtime.create_persistence().repository.list_runs()
                })
            except Exception as exc:
                return self._json(500, {"error": "persistence_list_failed", "detail": str(exc)})

        if path.startswith("/v1/persistence/events"):
            try:
                cursor = int(body.get("after", 0))
                run_id = body.get("run_id")
                events = self.runtime.create_persistence().repository.events_after(
                    cursor, run_id=run_id
                )
                return self._json(200, {"events": events})
            except Exception as exc:
                return self._json(500, {"error": "persistence_events_failed", "detail": str(exc)})

        if path == "/v1/context":
            self.runtime.context.update(**body)
            return self._json(200, self.runtime.context.snapshot())

        if path == "/v1/runs":
            loop = self.runtime.create_loop(body.get("request",""), body.get("run_id"))
            return self._json(200, loop.run(auto_apply=body.get("auto_apply", False)))

        if path.startswith("/v1/runs/") and path.endswith("/approve"):
            run_id = path.split("/")[3]
            return self._json(200, self.runtime.get_run(run_id).approve())

        if path.startswith("/v1/errors/") and path.endswith("/code"):
            error_id = path.split("/")[3]
            return self._json(200, self.runtime.code_intelligence.analyze_error(error_id))

        if path.startswith("/v1/errors/") and path.endswith("/diagnosis"):
            error_id = path.split("/")[3]
            return self._json(200, self.runtime.errors.diagnose(error_id))

        if path.startswith("/v1/runs/") and path.endswith("/deny"):
            run_id = path.split("/")[3]
            return self._json(200, self.runtime.get_run(run_id).deny())

        return self._json(404, {"error":"not_found"})

def create_server(runtime, host="127.0.0.1", port=8765):
    Handler.runtime = runtime
    return ThreadingHTTPServer((host, port), Handler)

def serve(runtime, host="127.0.0.1", port=8765):
    server = create_server(runtime, host, port)
    print(f"Berkios 2.1 API: http://{host}:{port}")
    server.serve_forever()
