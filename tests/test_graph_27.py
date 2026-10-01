from pathlib import Path
from berkios.graph.builder import ProjectGraphBuilder

def test_graph_builder(tmp_path: Path):
    (tmp_path / "a.py").write_text("import os\nclass A: pass\n", encoding="utf-8")
    graph = ProjectGraphBuilder(tmp_path).build()
    assert "file:a.py" in graph.nodes
    assert any(n.kind == "symbol" and n.label == "A" for n in graph.nodes.values())
    assert any(e.kind == "imports" for e in graph.edges)
