from __future__ import annotations

from test_remote_script import __version__


def test_main() -> None:
    assert isinstance(__version__, str)
