from __future__ import annotations
from berkios.graph.builder import ProjectGraphBuilder

def graph_snapshot(workspace):
    return ProjectGraphBuilder(workspace).build().to_dict()

def graph_related(workspace, node_id: str):
    graph = ProjectGraphBuilder(workspace).build()
    return [vars(node) for node in graph.related(node_id)]
