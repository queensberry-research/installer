from __future__ import annotations

from pathlib import Path

from installer.constants import CONFIGS


class TestConstants:
    def test_configs(self) -> None:
        assert isinstance(CONFIGS, Path)
        assert CONFIGS.is_dir()
        assert {p.name for p in CONFIGS.iterdir()} == {"config.toml", "proxmox", "ssh"}
