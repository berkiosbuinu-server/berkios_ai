import re
from .models import ErrorEvent, ErrorKind, ErrorSeverity

PYTHON_TRACE = re.compile(r'File "(.+?)", line (\d+)(?:, in .*)?')

class ErrorParser:
    """Transforme sorties d'outils et tracebacks en événements exploitables."""
    def parse_python(self, text, source="python"):
        events = []
        lines = text.splitlines()
        current = None
        for i, line in enumerate(lines):
            m = PYTHON_TRACE.search(line)
            if m:
                current = ErrorEvent(
                    message="Traceback Python",
                    kind=ErrorKind.RUNTIME,
                    source=source,
                    file=m.group(1),
                    line=int(m.group(2)),
                    traceback=text,
                )
                events.append(current)
            if line.startswith("SyntaxError:"):
                events.append(ErrorEvent(
                    message=line.split(":",1)[1].strip(),
                    kind=ErrorKind.SYNTAX,
                    source=source,
                    severity=ErrorSeverity.ERROR,
                    traceback=text,
                    file=current.file if current else None,
                    line=current.line if current else None,
                ))
            elif line.startswith("ModuleNotFoundError:") or line.startswith("ImportError:"):
                events.append(ErrorEvent(
                    message=line.split(":",1)[1].strip(),
                    kind=ErrorKind.IMPORT,
                    source=source,
                    traceback=text,
                    file=current.file if current else None,
                    line=current.line if current else None,
                ))
            elif line.startswith("TypeError:"):
                events.append(ErrorEvent(
                    message=line.split(":",1)[1].strip(),
                    kind=ErrorKind.TYPE,
                    source=source,
                    traceback=text,
                    file=current.file if current else None,
                    line=current.line if current else None,
                ))
            elif line.startswith("AssertionError"):
                events.append(ErrorEvent(
                    message=line,
                    kind=ErrorKind.TEST,
                    source=source,
                    traceback=text,
                    file=current.file if current else None,
                    line=current.line if current else None,
                ))
        return events

    def parse_command_result(self, argv, returncode, stdout="", stderr="", source="command"):
        if returncode == 0:
            return []
        text = stderr or stdout
        events = self.parse_python(text, source=source)
        if not events:
            kind = ErrorKind.TEST if "test" in " ".join(argv).lower() else ErrorKind.TOOL
            events = [ErrorEvent(
                message=(text.strip().splitlines()[-1] if text.strip() else f"Command exited with {returncode}"),
                kind=kind,
                source=source,
                command=argv,
                stdout=stdout,
                stderr=stderr,
            )]
        for event in events:
            event.command = argv
            event.stdout = stdout
            event.stderr = stderr
        return events
