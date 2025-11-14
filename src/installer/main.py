from __future__ import annotations

from logging import getLogger
from pathlib import Path

import click
from click import command, option
from utilities.click import CONTEXT_SETTINGS_HELP_OPTION_NAMES
from utilities.logging import basic_config

from installer import __version__
from installer.constants import CONFIGS_PROXMOX_STORAGE_CFG, NONROOT
from installer.envs.proxmox import setup_proxmox
from installer.installs import install_docker
from installer.utilities import has_non_root, is_lxc, is_proxmox, run

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
    "--proxmox-storage-cfg",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    default=CONFIGS_PROXMOX_STORAGE_CFG,
    show_default=True,
    help="Proxmox `storage.cfg`",
)
@option(
    "--proxmox-pbs-password",
    type=str,
    default=None,
    show_default=True,
    help="Proxmox `pbs-data` password",
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
def _main(
    *,
    proxmox: bool,
    proxmox_storage_cfg: Path,
    proxmox_pbs_password: str,
    create_non_root: bool,
    docker: bool,
) -> None:
    _LOGGER.info("Running installer %s...", __version__)
    if proxmox:
        setup_proxmox(
            storage_cfg=proxmox_storage_cfg, pbs_password=proxmox_pbs_password
        )
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


if __name__ == "__main__":
    basic_config(obj=_LOGGER, hostname=True)
    _main()
