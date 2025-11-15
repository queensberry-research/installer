from __future__ import annotations

from logging import getLogger
from pathlib import Path

from utilities.os import is_pytest

from installer.constants import CONFIGS, CONFIGS_PROFILE, CONFIGS_SSH, NONROOT, ROOT
from installer.settings import SETTINGS
from installer.utilities import (
    copy,
    get_subnet,
    has_non_root,
    is_copied,
    is_immutable,
    run,
    set_immutable,
    substitute,
    systemctl_restart,
    touch,
)

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
    _set_password_one(ROOT, password)
    if has_non_root():
        _set_password_one(NONROOT, password)
    else:
        _LOGGER.info("Skipping %r; user does not exist", NONROOT)


def _set_password_one(username: str, password: str, /) -> None:
    _LOGGER.info("Setting %r password...", ROOT)
    run(f"echo '{username}:{password}' | chpasswd")


def setup_git() -> None:
    src = CONFIGS / "git/config"
    dest = Path("/etc/gitconfig")
    if is_copied(src, dest):
        _LOGGER.info("%r -> %r is already copied", str(src), str(dest))
    else:
        _LOGGER.info("Copying %r -> %r...", str(src), str(dest))
        copy(src, dest)


def setup_profile() -> None:
    src = CONFIGS_PROFILE / "default.sh"
    dest = Path("/etc/profile.d/default.sh")
    if is_copied(src, dest):
        _LOGGER.info("%r -> %r is already copied", str(src), str(dest))
    else:
        _LOGGER.info("Copying %r -> %r...", str(src), str(dest))
        copy(src, dest)


def setup_resolv_conf() -> None:
    try:
        subnet = get_subnet()
    except (KeyError, ValueError):
        _LOGGER.warning("Unable to determine subnet")
        return
    src = CONFIGS / "networking/resolv.conf"
    text = substitute(src.read_text(), n=subnet.n, subnet=subnet.value)
    dest = Path("/etc/resolv.conf")
    if is_copied(text, dest) and is_immutable(dest):
        _LOGGER.info("%r -> %r is already copied", str(src), str(dest))
    else:
        _LOGGER.info("Copying %r -> %r...", str(src), str(dest))
        copy(text, dest)
        set_immutable(dest)


def setup_subnet_env_var() -> None:
    try:
        subnet = get_subnet()
    except (KeyError, ValueError):
        _LOGGER.warning("Unable to determine subnet")
        return
    src = CONFIGS_PROFILE / "subnet.sh"
    text = substitute(src.read_text(), subnet=subnet.value)
    dest = Path("/etc/profile.d/subnet.sh")
    if is_copied(text, dest):
        _LOGGER.info("%r -> %r is already copied", str(src), str(dest))
    else:
        _LOGGER.info("Copying %r -> %r...", str(src), str(dest))
        copy(text, dest)


def setup_ssh_authorized_keys(*srcs: Path) -> None:
    src_desc = ", ".join(map(str, srcs))
    text = "\n".join(s.read_text() for s in srcs)
    dest = Path("/etc/ssh/authorized_keys")
    if is_copied(text, dest):
        _LOGGER.info("%r -> %r is already copied", src_desc, str(dest))
    else:
        _LOGGER.info("Writing %r -> %r...", src_desc, str(dest))
        copy(text, dest)


def setup_ssh_config_d() -> None:
    src = CONFIGS_SSH / "ssh_config.d/default.conf"
    dest = Path("/etc/ssh/ssh_config.d/default.conf")
    if is_copied(src, dest):
        _LOGGER.info("%r -> %r is already copied", str(src), str(dest))
    else:
        _LOGGER.info("Copying %r -> %r...", str(src), str(dest))
        copy(src, dest)
        systemctl_restart("sshd")


def setup_ssh_known_hosts() -> None:
    # after `resolv.conf`
    if is_pytest():
        return
    path = Path("/etc/ssh/known_hosts")
    touch(path)
    for known_host in SETTINGS.ssh.known_hosts:
        _setup_ssh_known_hosts_one(known_host.hostname, port=known_host.port)
    systemctl_restart("sshd")


def _setup_ssh_known_hosts_one(hostname: str, /, *, port: int | None = None) -> None:
    _ = run(f"ssh-keygen -R {hostname}", failable=True)
    parts: list[str] = ["ssh-keyscan -H -q -t ed25519"]
    if port is not None:
        parts.append(f"-p {port}")
    parts.append(f"{hostname} >> /etc/ssh/known_hosts")
    cmd = " ".join(parts)
    for _ in range(1, SETTINGS.ssh.max_tries + 1):
        if run(cmd, failable=True):
            systemctl_restart("sshd")
            return
    msg = f"{cmd!r} failed after {SETTINGS.ssh.max_tries} tries"
    raise RuntimeError(msg)


def setup_sshd_config_d() -> None:
    src = CONFIGS_SSH / "sshd_config.d/default.conf"
    dest = Path("/etc/ssh/sshd_config.d/default.conf")
    if is_copied(src, dest):
        _LOGGER.info("%r -> %r is already copied", str(src), str(dest))
    else:
        _LOGGER.info("Copying %r -> %r...", str(src), str(dest))
        copy(src, dest)
        systemctl_restart("sshd")


__all__ = [
    "create_non_root",
    "set_password",
    "setup_git",
    "setup_profile",
    "setup_resolv_conf",
    "setup_ssh_authorized_keys",
    "setup_ssh_config_d",
    "setup_ssh_known_hosts",
    "setup_sshd_config_d",
    "setup_subnet_env_var",
]
