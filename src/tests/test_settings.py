from __future__ import annotations

from installer.settings import SETTINGS, _Settings


class TestSettings:
    def test_main(self) -> None:
        assert isinstance(SETTINGS, _Settings)
