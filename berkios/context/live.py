class LiveContext:
    def __init__(self):
        self.data = {
            "workspace": None, "active_file": None, "active_content": None,
            "selection": None, "cursor": None, "diagnostics": [],
            "recent_files": []
        }

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.data:
                self.data[key] = value

    def semantic_context(self, semantic_memory, request, files=None):
        return semantic_memory.context(request, files)

    def compose(self, request="", max_chars=12000):
        parts = [f"REQUEST:\n{request}"]
        for key, value in self.data.items():
            if value not in (None, "", [], {}):
                parts.append(f"{key.upper()}:\n{value}")
        return "\n\n".join(parts)[:max_chars]

    def snapshot(self):
        return dict(self.data)
