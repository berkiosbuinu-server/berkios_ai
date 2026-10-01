from berkios.runtime.app import create_runtime

def test_semantic_memory(tmp_path):
    rt=create_runtime(tmp_path)
    item=rt.semantic_memory.remember(
        "architecture",
        "Le moteur agentique ne modifie jamais l'éditeur sans approbation.",
        tags=["agent","approval"],
        files=["berkios/agent/loop.py"]
    )
    assert item["category"]=="architecture"
    result=rt.semantic_memory.context("approbation moteur agentique",
                                       ["berkios/agent/loop.py"])
    assert result["knowledge"]

def test_project_relations(tmp_path):
    (tmp_path/"main.py").write_text("import os\n",encoding="utf-8")
    rt=create_runtime(tmp_path)
    result=rt.project_semantics.summarize()
    assert result["python_files"] >= 1
    assert result["relations"]
