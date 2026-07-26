import uuid

import common.calibration as calibration_module


def _write_calibration_file(tmp_path, project_id, calibration_id, content):
    directory = tmp_path / "projects" / project_id / "servo_calibration"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{calibration_id}.json").write_text(content)


def test_load_calibration_missing_file_returns_empty_dict(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CALIBRATION_ID", "unit-a")
    assert calibration_module.load_calibration("skeleton") == {}


def test_load_calibration_returns_empty_without_an_id(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("CALIBRATION_ID", raising=False)

    _write_calibration_file(
        tmp_path, "skeleton", "unit-a", '{"head": {"min": 10, "max": 170, "rest": 90}}'
    )

    assert calibration_module.load_calibration("skeleton") == {}


def test_load_calibration_invalid_json_returns_empty_dict(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CALIBRATION_ID", "unit-a")
    _write_calibration_file(tmp_path, "skeleton", "unit-a", "not json")

    assert calibration_module.load_calibration("skeleton") == {}


def test_load_calibration_returns_only_current_unit_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CALIBRATION_ID", "unit-a")
    _write_calibration_file(
        tmp_path, "skeleton", "unit-a", '{"head": {"min": 10, "max": 170, "rest": 90}}'
    )
    _write_calibration_file(
        tmp_path, "skeleton", "unit-b", '{"head": {"min": 20, "max": 160, "rest": 80}}'
    )

    assert calibration_module.load_calibration("skeleton") == {
        "head": {"min": 10, "max": 170, "rest": 90}
    }


def test_has_calibration_false_without_saved_data(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("CALIBRATION_ID", raising=False)
    assert calibration_module.has_calibration("skeleton") is False


def test_has_calibration_true_when_unit_file_exists(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CALIBRATION_ID", "unit-a")
    _write_calibration_file(
        tmp_path, "skeleton", "unit-a", '{"head": {"min": 10, "max": 170, "rest": 90}}'
    )

    assert calibration_module.has_calibration("skeleton") is True


def test_get_or_create_calibration_id_reuses_existing_env_value(monkeypatch):
    monkeypatch.setenv("CALIBRATION_ID", "existing-id")

    def fail_if_called(*args, **kwargs):
        raise AssertionError("set_key should not be called when an id already exists")

    monkeypatch.setattr(calibration_module, "set_key", fail_if_called)

    assert calibration_module.get_or_create_calibration_id() == "existing-id"


def test_get_or_create_calibration_id_generates_and_persists_new_one(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("CALIBRATION_ID", raising=False)
    monkeypatch.setattr(calibration_module, "find_dotenv", lambda: str(tmp_path / ".env"))

    first_id = calibration_module.get_or_create_calibration_id()
    assert uuid.UUID(first_id)  # a real UUIDv4, not a hash
    assert calibration_module.os.environ["CALIBRATION_ID"] == first_id
    assert first_id in (tmp_path / ".env").read_text()

    # Calling it again must reuse the same id, not generate a new one.
    second_id = calibration_module.get_or_create_calibration_id()
    assert second_id == first_id


def test_save_calibration_creates_new_id_and_file_when_none_exists(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("CALIBRATION_ID", raising=False)
    monkeypatch.setattr(calibration_module, "find_dotenv", lambda: str(tmp_path / ".env"))

    calibration_module.save_calibration("skeleton", {"head": {"min": 10, "max": 170, "rest": 90}})

    generated_id = calibration_module.os.environ["CALIBRATION_ID"]
    assert calibration_module.load_calibration("skeleton") == {
        "head": {"min": 10, "max": 170, "rest": 90}
    }
    assert (
        tmp_path / "projects" / "skeleton" / "servo_calibration" / f"{generated_id}.json"
    ).exists()


def test_save_calibration_merges_into_existing_file_without_touching_others(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CALIBRATION_ID", "unit-a")
    _write_calibration_file(
        tmp_path, "skeleton", "unit-a", '{"head": {"min": 10, "max": 170, "rest": 90}}'
    )
    _write_calibration_file(
        tmp_path, "skeleton", "unit-b", '{"head": {"min": 20, "max": 160, "rest": 80}}'
    )

    calibration_module.save_calibration("skeleton", {"arm": {"min": 0, "max": 180, "rest": 90}})

    assert calibration_module.load_calibration("skeleton") == {
        "head": {"min": 10, "max": 170, "rest": 90},
        "arm": {"min": 0, "max": 180, "rest": 90},
    }

    monkeypatch.setenv("CALIBRATION_ID", "unit-b")
    assert calibration_module.load_calibration("skeleton") == {
        "head": {"min": 20, "max": 160, "rest": 80}
    }


def test_generate_calibration_id_is_a_uuid4():
    generated = calibration_module._generate_calibration_id()
    assert uuid.UUID(generated).version == 4
