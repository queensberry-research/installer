from __future__ import annotations

from logging import getLogger
from shutil import which

from installer.constants import NONROOT
from installer.utilities import has_non_root, run

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
    if has_non_root():
        run(f"usermod -aG docker {NONROOT}")


__all__ = ["install_docker"]
