from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from berkios.graph.intelligence import ProjectGraphIntelligence

@dataclass
class ImpactAwarePlan:
    request: str
    targets: list[str] = field(default_factory=list)
    affected_files: list[str] = field(default_factory=list)
    affected_symbols: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "request": self.request,
            "targets": self.targets,
            "affected_files": self.affected_files,
            "affected_symbols": self.affected_symbols,
            "risks": self.risks,
            "context": self.context,
        }

class ImpactAwarePlanner:
    def __init__(self, workspace):
        self.workspace = workspace
        self.graph = ProjectGraphIntelligence(workspace)

    def analyze_targets(self, targets: list[str], request: str = "") -> ImpactAwarePlan:
        files = set()
        symbols = set()
        contexts = []
        risks = []

        for target in targets:
            report = self.graph.impact(target, depth=2)
            files.update(report.affected_files)
            symbols.update(report.affected_symbols)
            contexts.append({
                "target": target,
                "affected_files": report.affected_files,
                "affected_symbols": report.affected_symbols,
            })

            if len(report.affected_files) >= 5:
                risks.append(f"large_impact:{target}")
            if len(report.affected_symbols) >= 10:
                risks.append(f"symbol_cascade:{target}")

        return ImpactAwarePlan(
            request=request,
            targets=targets,
            affected_files=sorted(files),
            affected_symbols=sorted(symbols),
            risks=sorted(set(risks)),
            context={"impacts": contexts},
        )
