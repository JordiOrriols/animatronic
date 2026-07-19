import pytest

from common.logger import Logger


@pytest.mark.parametrize(
    ("method_name", "expected_prefix", "enable_debug"),
    [("log", "Log:", True), ("info", "Info:", False), ("error", "ERROR:", False)],
)
def test_logger_emits_messages(method_name, expected_prefix, enable_debug, capsys):
    logger = Logger("demo")
    if enable_debug:
        logger.debug()

    getattr(logger, method_name)("hello")
    captured = capsys.readouterr()
    assert expected_prefix in captured.out
    assert "demo" in captured.out


def test_logger_log_is_silent_without_debug(capsys):
    logger = Logger("demo")
    logger.log("hello")
    captured = capsys.readouterr()
    assert captured.out == ""
