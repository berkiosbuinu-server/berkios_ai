API_VERSION = "v1"

def health_payload():
    return {"status": "ok", "api_version": API_VERSION, "runtime_version": "2.1.0"}
