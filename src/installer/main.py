from __future__ import annotations

from logging import getLogger
from pathlib import Path

import click
from click import command, option
from utilities.click import CONTEXT_SETTINGS_HELP_OPTION_NAMES
from utilities.logging import basic_config

import installer.setups
from installer import __version__
from installer.constants import CONFIGS_PROXMOX_STORAGE_CFG, CONFIGS_SSH_AUTHORIZED_KEYS
from installer.envs.proxmox import setup_proxmox
from installer.installs import install_docker, install_starship
from installer.setups import (
    set_password,
    setup_git,
    setup_profile,
    setup_ssh_authorized_keys,
    setup_ssh_config_d,
    setup_ssh_known_hosts,
    setup_sshd_config_d,
    setup_subnet_env_var,
)
from installer.utilities import is_lxc, is_proxmox, is_vm

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
@option("--password", type=str, default=None, show_default=True, help="Password")
@option(
    "--ssh-authorized-keys",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    default=CONFIGS_SSH_AUTHORIZED_KEYS,
    show_default=True,
    help="SSH authorized keys",
)
@option(
    "--docker/--no-docker",
    is_flag=True,
    default=is_lxc() or is_vm(),
    show_default=True,
    help="Install Docker",
)
def _main(
    *,
    proxmox: bool,
    proxmox_storage_cfg: Path,
    proxmox_pbs_password: str | None,
    create_non_root: bool,
    password: str | None,
    ssh_authorized_keys: Path,
    docker: bool,
) -> None:
    _LOGGER.info("Running installer %s...", __version__)
    if proxmox:
        setup_proxmox(
            storage_cfg=proxmox_storage_cfg, pbs_password=proxmox_pbs_password
        )
    if create_non_root:
        installer.setups.create_non_root()
    set_password(password=password)
    setup_git()
    setup_profile()
    setup_ssh_authorized_keys(ssh_authorized_keys)
    setup_ssh_config_d()
    setup_ssh_known_hosts()
    setup_sshd_config_d()
    setup_subnet_env_var()
    install_starship()
    if docker:
        install_docker()
    _LOGGER.info("Finished running installer %s", __version__)


if __name__ == "__main__":
    basic_config(obj=_LOGGER, hostname=True)
    _main()
