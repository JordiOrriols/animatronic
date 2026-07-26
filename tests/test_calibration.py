import subprocess
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


def test_git_commit_and_push_returns_false_without_calibration_id(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("CALIBRATION_ID", raising=False)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("git should never be invoked without a calibration id")

    monkeypatch.setattr(calibration_module.subprocess, "run", fail_if_called)

    assert calibration_module.git_commit_and_push("skeleton") is False


def test_git_commit_and_push_success(monkeypatch):
    monkeypatch.setenv("CALIBRATION_ID", "unit-a")
    calls = []

    def fake_run(args, check=False, capture_output=False, text=False):
        calls.append(args)
        if args[:2] == ["git", "diff"]:
            return subprocess.CompletedProcess(args, returncode=1)
        return subprocess.CompletedProcess(args, returncode=0)

    monkeypatch.setattr(calibration_module.subprocess, "run", fake_run)

    result = calibration_module.git_commit_and_push("skeleton")

    assert result is True
    assert calls[0][:2] == ["git", "checkout"]
    assert calls[1] == ["git", "add", "projects/skeleton/servo_calibration/unit-a.json"]
    assert calls[3][:2] == ["git", "commit"]
    assert calls[4][:2] == ["git", "push"]
    assert calls[-1] == ["git", "checkout", "main"]


def test_git_commit_and_push_skips_commit_when_nothing_staged(monkeypatch):
    monkeypatch.setenv("CALIBRATION_ID", "unit-a")
    calls = []

    def fake_run(args, check=False, capture_output=False, text=False):
        calls.append(args)
        if args[:2] == ["git", "diff"]:
            return subprocess.CompletedProcess(args, returncode=0)
        return subprocess.CompletedProcess(args, returncode=0)

    monkeypatch.setattr(calibration_module.subprocess, "run", fake_run)

    result = calibration_module.git_commit_and_push("skeleton")

    assert result is False
    assert not any(args[:2] == ["git", "commit"] for args in calls)
    assert not any(args[:2] == ["git", "push"] for args in calls)
    assert calls[-1] == ["git", "checkout", "main"]


def test_git_commit_and_push_never_raises_on_failure(monkeypatch):
    monkeypatch.setenv("CALIBRATION_ID", "unit-a")
    calls = []

    def fake_run(args, check=False, capture_output=False, text=False):
        calls.append(args)
        if args[:2] == ["git", "checkout"] and args[-1] != "main":
            raise subprocess.CalledProcessError(1, args)
        return subprocess.CompletedProcess(args, returncode=0)

    monkeypatch.setattr(calibration_module.subprocess, "run", fake_run)

    result = calibration_module.git_commit_and_push("skeleton")

    assert result is False
    # Must still attempt to land back on main even though the branch checkout failed.
    assert calls[-1] == ["git", "checkout", "main"]


def test_git_commit_and_push_handles_missing_git_binary(monkeypatch):
    monkeypatch.setenv("CALIBRATION_ID", "unit-a")

    def fake_run(args, check=False, capture_output=False, text=False):
        raise FileNotFoundError("git not found")

    monkeypatch.setattr(calibration_module.subprocess, "run", fake_run)

    result = calibration_module.git_commit_and_push("skeleton")
    assert result is False
