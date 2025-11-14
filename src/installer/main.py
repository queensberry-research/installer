from __future__ import annotations

from logging import getLogger
from pathlib import Path

from click import command, option
from utilities.click import CONTEXT_SETTINGS_HELP_OPTION_NAMES
from utilities.logging import basic_config

from installer import __version__
from installer.constants import CONFIGS, NONROOT
from installer.installs import install_docker
from installer.settings import SETTINGS
from installer.utilities import copy, has_non_root, is_lxc, is_proxmox, run

_LOGGER = getLogger(__name__)


@command(**CONTEXT_SETTINGS_HELP_OPTION_NAMES)
@option(
    "--proxmox/--no-proxmox",
    is_flag=True,
    default=is_proxmox(),
    show_default=True,
    help="Set up Proxmox",
)
@option(
    "--create-non-root/--no-create-non-root",
    is_flag=True,
    default=False,
    show_default=True,
    help="Create 'nonroot'",
)
@option(
    "--docker/--no-docker",
    is_flag=True,
    default=is_lxc(),
    show_default=True,
    help="Install Docker",
)
def _main(*, proxmox: bool, create_non_root: bool, docker: bool) -> None:
    _LOGGER.info("Running installer %s...", __version__)
    if proxmox:
        _setup_proxmox()
    if create_non_root:
        _create_non_root()
    if docker:
        install_docker()
    _LOGGER.info("Finished running installer %s", __version__)


def _create_non_root() -> None:
    if has_non_root():
        _LOGGER.info("%r already exists", NONROOT)
    else:
        _LOGGER.info("Creating %r...", NONROOT)
        run(f"useradd --create-home --shell /bin/bash {NONROOT}")
        run(f"usermod -aG sudo {NONROOT}")


def _setup_proxmox() -> None:
    for name in ["ceph", "pve-enterprise"]:
        Path(f"/etc/apt/sources.list.d/{name}.sources").unlink(missing_ok=True)
    proxmox = CONFIGS / "proxmox"
    copy(proxmox / "storage.cfg", Path("/etc/pve/storage.cfg"))
    copy(
        proxmox / "pbs-data.pw",
        Path("/etc/pve/priv/storage/pbs-data.pw"),
        password=SETTINGS.pbs.get_secret_value(),
    )


if __name__ == "__main__":
    basic_config(obj=_LOGGER, hostname=True)
    _main()
