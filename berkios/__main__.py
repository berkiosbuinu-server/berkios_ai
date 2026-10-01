from .runtime.app import create_runtime
from .api.server import serve

if __name__ == "__main__":
    runtime = create_runtime()
    serve(runtime)
