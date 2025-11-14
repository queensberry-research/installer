from __future__ import annotations

from logging import getLogger

from click import command, option
from utilities.click import CONTEXT_SETTINGS_HELP_OPTION_NAMES
from utilities.logging import basic_config

from installer import __version__
from installer.constants import NONROOT
from installer.utilities import run

_LOGGER = getLogger(__name__)


@command(**CONTEXT_SETTINGS_HELP_OPTION_NAMES)
@option("--asdf", is_flag=True, default=False, show_default=True)
@option(
    "--create-non-root",
    is_flag=True,
    default=False,
    show_default=True,
    help="Create 'nonroot'",
)
def _main(*, asdf: bool, create_non_root: bool = False) -> None:
    _LOGGER.info("Running installer %s...", __version__)
    _LOGGER.info("Got 'asdf' = %s", asdf)
    if create_non_root:
        _create_non_root()
    _LOGGER.info("Finished running installer %s", __version__)


def _create_non_root() -> None:
    if _has_non_root():
        _LOGGER.info("%r already exists", NONROOT)
    else:
        _LOGGER.info("Creating %r...", NONROOT)
        run(f"useradd --create-home --shell /bin/bash {NONROOT}")
        run(f"usermod -aG sudo {NONROOT}")


def _has_non_root() -> bool:
    return run(f"id -u {NONROOT}", failable=True)


if __name__ == "__main__":
    basic_config(obj=_LOGGER, hostname=True)
    _main()
