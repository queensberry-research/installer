from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from typing import cast

CONFIGS = cast("Path", files("configs").joinpath("z")).parent
CONFIGS_BASH = CONFIGS / "bash"
CONFIGS_PROXMOX = CONFIGS / "proxmox"
CONFIGS_PROXMOX_STORAGE_CFG = CONFIGS_PROXMOX / "storage.cfg"
CONFIGS_SSH = CONFIGS / "ssh"
CONFIGS_SSH_AUTHORIZED_KEYS = CONFIGS_SSH / "authorized_keys"


ROOT = "root"
NONROOT = "nonroot"
HOME_ROOT = Path("/root")
HOME_NONROOT = Path("/home/nonroot")


__all__ = [
    "CONFIGS",
    "CONFIGS_BASH",
    "CONFIGS_PROXMOX",
    "CONFIGS_PROXMOX_STORAGE_CFG",
    "CONFIGS_SSH",
    "CONFIGS_SSH_AUTHORIZED_KEYS",
    "HOME_NONROOT",
    "HOME_ROOT",
    "NONROOT",
    "ROOT",
]
