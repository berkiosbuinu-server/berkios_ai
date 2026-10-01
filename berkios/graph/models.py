from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import json
from pathlib import Path

@dataclass
class GraphNode:
    id: str
    kind: str
    label: str
    data: dict[str, Any] = field(default_factory=dict)

@dataclass
class GraphEdge:
    source: str
    target: str
    kind: str
    data: dict[str, Any] = field(default_factory=dict)

class ProjectGraph:
    def __init__(self, workspace: Path):
        self.workspace = Path(workspace)
        self.path = self.workspace / ".berkios" / "graph.json"
        self.nodes: dict[str, GraphNode] = {}
        self.edges: list[GraphEdge] = []

    def add_node(self, node: GraphNode) -> GraphNode:
        self.nodes[node.id] = node
        return node

    def add_edge(self, edge: GraphEdge) -> GraphEdge:
        if edge.source in self.nodes and edge.target in self.nodes:
            self.edges.append(edge)
        return edge

    def related(self, node_id: str) -> list[GraphNode]:
        ids = set()
        for edge in self.edges:
            if edge.source == node_id:
                ids.add(edge.target)
            elif edge.target == node_id:
                ids.add(edge.source)
        return [self.nodes[i] for i in ids if i in self.nodes]

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [vars(n) for n in self.nodes.values()],
            "edges": [vars(e) for e in self.edges],
        }

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    def load(self) -> None:
        if not self.path.exists():
            return
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.nodes = {n["id"]: GraphNode(**n) for n in data.get("nodes", [])}
        self.edges = [GraphEdge(**e) for e in data.get("edges", [])]
