def test_persistence_modules_import():
    from berkios.persistence import Database, PersistenceRepository
    from berkios.persistence.redis_bus import RedisEventBus
    assert Database is not None
    assert PersistenceRepository is not None
    assert RedisEventBus is not None

def test_local_repository_roundtrip(tmp_path):
    from berkios.persistence import Database, PersistenceRepository
    db = Database(f"sqlite:///{tmp_path / 'test.db'}")
    repo = PersistenceRepository(db)
    repo.upsert_run("run-1", "created", {"hello": "world"}, "/tmp/project")
    got = repo.get_run("run-1")
    assert got["state"] == "created"
    assert got["payload"]["hello"] == "world"
    event_id = repo.add_event("run.created", {"ok": True}, "run-1")
    assert repo.events_after(0, "run-1")[0]["id"] == event_id
