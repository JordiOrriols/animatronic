import subprocess

import common.calibration as calibration_module


def test_load_calibration_missing_file_returns_empty_dict(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CALIBRATION_HASH", "unit-a")
    assert calibration_module.load_calibration("skeleton") == {}


def test_load_calibration_returns_empty_without_a_hash(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("CALIBRATION_HASH", raising=False)

    (tmp_path / "projects" / "skeleton").mkdir(parents=True)
    (tmp_path / "projects" / "skeleton" / "servo_calibration.json").write_text(
        '{"unit-a": {"head": {"min": 10, "max": 170, "rest": 90}}}'
    )

    assert calibration_module.load_calibration("skeleton") == {}


def test_load_calibration_invalid_json_returns_empty_dict(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CALIBRATION_HASH", "unit-a")
    (tmp_path / "projects" / "skeleton").mkdir(parents=True)
    (tmp_path / "projects" / "skeleton" / "servo_calibration.json").write_text("not json")

    assert calibration_module.load_calibration("skeleton") == {}


def test_load_calibration_returns_only_current_unit_profile(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CALIBRATION_HASH", "unit-a")
    (tmp_path / "projects" / "skeleton").mkdir(parents=True)
    (tmp_path / "projects" / "skeleton" / "servo_calibration.json").write_text(
        '{"unit-a": {"head": {"min": 10, "max": 170, "rest": 90}},'
        ' "unit-b": {"head": {"min": 20, "max": 160, "rest": 80}}}'
    )

    assert calibration_module.load_calibration("skeleton") == {
        "head": {"min": 10, "max": 170, "rest": 90}
    }


def test_get_or_create_calibration_hash_reuses_existing_env_value(monkeypatch):
    monkeypatch.setenv("CALIBRATION_HASH", "existing-hash")

    def fail_if_called(*args, **kwargs):
        raise AssertionError("set_key should not be called when a hash already exists")

    monkeypatch.setattr(calibration_module, "set_key", fail_if_called)

    assert calibration_module.get_or_create_calibration_hash() == "existing-hash"


def test_get_or_create_calibration_hash_generates_and_persists_new_one(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("CALIBRATION_HASH", raising=False)
    monkeypatch.setattr(calibration_module, "find_dotenv", lambda: str(tmp_path / ".env"))

    first_hash = calibration_module.get_or_create_calibration_hash()
    assert first_hash
    assert calibration_module.os.environ["CALIBRATION_HASH"] == first_hash
    assert first_hash in (tmp_path / ".env").read_text()

    # Calling it again must reuse the same hash, not generate a new one.
    second_hash = calibration_module.get_or_create_calibration_hash()
    assert second_hash == first_hash


def test_save_calibration_creates_new_hash_profile_when_none_exists(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("CALIBRATION_HASH", raising=False)
    monkeypatch.setattr(calibration_module, "find_dotenv", lambda: str(tmp_path / ".env"))
    (tmp_path / "projects" / "skeleton").mkdir(parents=True)

    calibration_module.save_calibration("skeleton", {"head": {"min": 10, "max": 170, "rest": 90}})

    generated_hash = calibration_module.os.environ["CALIBRATION_HASH"]
    assert calibration_module.load_calibration("skeleton") == {
        "head": {"min": 10, "max": 170, "rest": 90}
    }
    profiles = calibration_module._load_profiles("skeleton")
    assert set(profiles.keys()) == {generated_hash}


def test_save_calibration_merges_into_existing_profile_without_touching_others(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CALIBRATION_HASH", "unit-a")
    (tmp_path / "projects" / "skeleton").mkdir(parents=True)
    (tmp_path / "projects" / "skeleton" / "servo_calibration.json").write_text(
        '{"unit-a": {"head": {"min": 10, "max": 170, "rest": 90}},'
        ' "unit-b": {"head": {"min": 20, "max": 160, "rest": 80}}}'
    )

    calibration_module.save_calibration("skeleton", {"arm": {"min": 0, "max": 180, "rest": 90}})

    profiles = calibration_module._load_profiles("skeleton")
    assert profiles["unit-a"] == {
        "head": {"min": 10, "max": 170, "rest": 90},
        "arm": {"min": 0, "max": 180, "rest": 90},
    }
    assert profiles["unit-b"] == {"head": {"min": 20, "max": 160, "rest": 80}}


def test_generate_calibration_hash_is_a_sha256_prefix():
    generated = calibration_module._generate_calibration_hash()
    assert len(generated) == 12
    assert all(char in "0123456789abcdef" for char in generated)


def test_git_commit_and_push_success(monkeypatch):
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
    assert calls[1] == ["git", "add", "projects/skeleton/servo_calibration.json"]
    assert calls[3][:2] == ["git", "commit"]
    assert calls[4][:2] == ["git", "push"]
    assert calls[-1] == ["git", "checkout", "main"]


def test_git_commit_and_push_skips_commit_when_nothing_staged(monkeypatch):
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
    def fake_run(args, check=False, capture_output=False, text=False):
        raise FileNotFoundError("git not found")

    monkeypatch.setattr(calibration_module.subprocess, "run", fake_run)

    result = calibration_module.git_commit_and_push("skeleton")
    assert result is False
