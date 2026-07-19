import pytest

from common.logger import Logger


@pytest.mark.parametrize(
    ("method_name", "expected_prefix"),
    [("log", "Log:"), ("info", "Info:"), ("error", "ERROR:")],
)
def test_logger_emits_messages(method_name, expected_prefix, capsys):
    logger = Logger("demo")
    getattr(logger, method_name)("hello")
    captured = capsys.readouterr()
    assert expected_prefix in captured.out
    assert "demo" in captured.out
