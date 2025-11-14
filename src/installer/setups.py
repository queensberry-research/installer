from __future__ import annotations

from logging import getLogger
from pathlib import Path

from utilities.os import is_pytest

from installer.constants import CONFIGS_SSH, NONROOT, ROOT
from installer.utilities import copy, has_non_root, is_copied, run

_LOGGER = getLogger(__name__)


def create_non_root() -> None:
    if has_non_root():
        _LOGGER.info("%r already exists", NONROOT)
        return
    _LOGGER.info("Creating %r...", NONROOT)
    run(f"useradd --create-home --shell /bin/bash {NONROOT}")
    run(f"usermod -aG sudo {NONROOT}")


def set_password(*, password: str | None = None) -> None:
    if password is None:
        _LOGGER.info("Skipping password(s)")
        return
    _LOGGER.info("Setting %r password...", ROOT)
    _set_password_one(ROOT, password)
    if has_non_root():
        _LOGGER.info("Setting %r password...", NONROOT)
        _set_password_one(NONROOT, password)
    else:
        _LOGGER.info("Skipping %r; user does not exist", NONROOT)


def _set_password_one(username: str, password: str, /) -> None:
    run(f"echo '{username}:{password}' | chpasswd")


def setup_ssh_authorized_keys(*srcs: Path) -> None:
    if is_pytest():
        return
    src_desc = ", ".join(map(str, srcs))
    text = "\n".join(s.read_text() for s in srcs)
    dest = Path("/etc/ssh/authorized_keys")
    if is_copied(text, dest):
        _LOGGER.info("%r -> %r is already copied", src_desc, str(dest))
    else:
        _LOGGER.info("Writing %r -> %r...", src_desc, str(dest))
        copy(text, dest)


def setup_ssh_config_d() -> None:
    if is_pytest():
        return
    src = CONFIGS_SSH / "ssh_config.d/default.conf"
    dest = Path("/etc/ssh/ssh_config.d/default.conf")
    if is_copied(src, dest):
        _LOGGER.info("%r -> %r is already copied", str(src), str(dest))
    else:
        _LOGGER.info("Copying %r -> %r...", str(src), str(dest))
        copy(src, dest)


def setup_sshd_config_d() -> None:
    if is_pytest():
        return
    src = CONFIGS_SSH / "sshd_config.d/default.conf"
    dest = Path("/etc/ssh/sshd_config.d/default.conf")
    if is_copied(src, dest):
        _LOGGER.info("%r -> %r is already copied", str(src), str(dest))
    else:
        _LOGGER.info("Copying %r -> %r...", str(src), str(dest))
        copy(src, dest)


__all__ = [
    "create_non_root",
    "set_password",
    "setup_ssh_authorized_keys",
    "setup_ssh_config_d",
    "setup_sshd_config_d",
]
