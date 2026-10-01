class Tool:
    name = ""
    permission = "project.read"
    requires_confirmation = False
    def execute(self, **kwargs):
        raise NotImplementedError
