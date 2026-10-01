from pathlib import Path
from berkios.providers.context import ContextAwareProvider

def test_context_aware_provider(tmp_path: Path):
    (tmp_path / "a.py").write_text("class A: pass\n", encoding="utf-8")
    provider = ContextAwareProvider(tmp_path)
    context = provider.build(
        "modify A",
        active_file="a.py",
        selection="class A",
        target_nodes=["file:a.py"],
    )
    data = context.to_dict()
    assert data["request"] == "modify A"
    assert data["ibook"]["active_file"] == "a.py"
    assert "a.py" in data["intelligence"]["affected_files"]
