from __future__ import annotations

from logging import getLogger
from pathlib import Path
from shutil import which

from installer.constants import CONFIGS, NONROOT
from installer.utilities import (
    apt_install,
    apt_installed,
    copy,
    has_non_root,
    is_copied,
    run,
)

_LOGGER = getLogger(__name__)


def install_docker() -> None:
    if which("docker") is None:
        _LOGGER.info("Installing 'docker'...")
        run(
            "for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do apt-get remove $pkg; done"
        )
        run("apt-get update")
        run("apt-get install -y ca-certificates curl")
        run("install -m 0755 -d /etc/apt/keyrings")
        run(
            "curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc"
        )
        run("chmod a+r /etc/apt/keyrings/docker.asc")
        run("""\
tee /etc/apt/sources.list.d/docker.sources <<DOCKEREOF
Types: deb
URIs: https://download.docker.com/linux/debian
Suites: $(. /etc/os-release && echo "$VERSION_CODENAME")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
DOCKEREOF""")
        run("apt-get update")
        run(
            "apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin"
        )
    else:
        _LOGGER.info("'docker' is already installed")
    if has_non_root():
        run(f"usermod -aG docker {NONROOT}")


def install_nfs_common() -> None:
    if apt_installed("nfs-common"):
        _LOGGER.info("'nfs-common' is already installed")
        return
    _LOGGER.info("Installing 'nfs-common'...")
    apt_install("nfs-common")


def install_starship() -> None:
    if which("starship") is None:
        _LOGGER.info("Installing 'starship'...")
        run("curl -sS https://starship.rs/install.sh | sh -s -- -b /usr/local/bin -y")
    else:
        _LOGGER.info("'starship' is already installed")
    src = CONFIGS / "starship/starship.toml"
    dest = Path("/etc/starship.toml")
    if is_copied(src, dest):
        _LOGGER.info("%r -> %r is already copied", str(src), str(dest))
    else:
        _LOGGER.info("Copying %r -> %r...", str(src), str(dest))
        copy(src, dest)


__all__ = ["install_docker", "install_nfs_common", "install_starship"]
