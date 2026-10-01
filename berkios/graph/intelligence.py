from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from .builder import ProjectGraphBuilder

@dataclass
class ImpactReport:
    target: str
    direct: list[dict[str, Any]] = field(default_factory=list)
    indirect: list[dict[str, Any]] = field(default_factory=list)
    affected_files: list[str] = field(default_factory=list)
    affected_symbols: list[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "target": self.target,
            "direct": self.direct,
            "indirect": self.indirect,
            "affected_files": self.affected_files,
            "affected_symbols": self.affected_symbols,
        }

class ProjectGraphIntelligence:
    def __init__(self, workspace):
        self.workspace = workspace
        self.graph = ProjectGraphBuilder(workspace).build()

    def related(self, node_id: str, depth: int = 1):
        seen = {node_id}
        frontier = [node_id]
        result = []
        for _ in range(max(1, depth)):
            next_frontier = []
            for current in frontier:
                for node in self.graph.related(current):
                    if node.id not in seen:
                        seen.add(node.id)
                        result.append(node)
                        next_frontier.append(node.id)
            frontier = next_frontier
            if not frontier:
                break
        return result

    def impact(self, node_id: str, depth: int = 2) -> ImpactReport:
        direct = self.related(node_id, 1)
        indirect = self.related(node_id, depth)
        files = []
        symbols = []
        for node in indirect:
            if node.kind == "file":
                files.append(node.label)
            elif node.kind == "symbol":
                symbols.append(node.label)
                path = node.data.get("file")
                if path and path not in files:
                    files.append(path)
        return ImpactReport(
            target=node_id,
            direct=[vars(n) for n in direct],
            indirect=[vars(n) for n in indirect],
            affected_files=sorted(set(files)),
            affected_symbols=sorted(set(symbols)),
        )

    def context_for(self, node_id: str, depth: int = 2) -> dict[str, Any]:
        report = self.impact(node_id, depth)
        return {
            "target": report.target,
            "affected_files": report.affected_files,
            "affected_symbols": report.affected_symbols,
            "related_nodes": report.indirect,
        }
