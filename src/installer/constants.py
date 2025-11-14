from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from typing import cast

CONFIGS = cast("Path", files("configs").joinpath("z")).parent
CONFIGS_PROXMOX = CONFIGS / "proxmox"
CONFIGS_PROXMOX_STORAGE_CFG = CONFIGS_PROXMOX / "storage.cfg"


NONROOT = "nonroot"
HOME_ROOT = Path("/root")
HOME_NONROOT = Path("/home/nonroot")


__all__ = [
    "CONFIGS",
    "CONFIGS_PROXMOX",
    "CONFIGS_PROXMOX_STORAGE_CFG",
    "HOME_NONROOT",
    "HOME_ROOT",
    "NONROOT",
]
