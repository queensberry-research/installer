from __future__ import annotations

from logging import basicConfig, getLogger
from socket import gethostname

LOGGING_FORMAT = (
    f"[{{asctime}} ❯ {gethostname()} ❯ {{module}}:{{funcName}}:{{lineno}}] {{message}}"  # noqa: RUF001
)
basicConfig(format=LOGGING_FORMAT, datefmt="%Y-%m-%d %H:%M:%S", style="{", level="INFO")
_LOGGER = getLogger(__name__)
# THIS MODULE CANNOT CONTAIN ANY THIRD PARTY IMPORTS
