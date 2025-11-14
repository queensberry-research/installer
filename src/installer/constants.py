from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from typing import cast

CONFIGS = cast("Path", files("configs").joinpath("z")).parent
NONROOT = "nonroot"
HOME_ROOT = Path("/root")
HOME_NONROOT = Path("/home/nonroot")


__all__ = ["CONFIGS", "HOME_NONROOT", "HOME_ROOT", "NONROOT"]
