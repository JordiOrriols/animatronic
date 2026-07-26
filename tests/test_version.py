import common.version as version_module


def test_get_version_reads_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".version").write_text("1.2.3\n")
    assert version_module.get_version() == "1.2.3"


def test_get_version_defaults_when_file_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert version_module.get_version() == "0.0.0"


def test_get_version_defaults_when_file_empty(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".version").write_text("   \n")
    assert version_module.get_version() == "0.0.0"
