from __future__ import annotations

from logging import getLogger

from click import command
from utilities.logging import basic_config

from test_remote_script import __version__

_LOGGER = getLogger(__name__)


@command()
def _main() -> None:
    basic_config(obj=_LOGGER, hostname=True)
    _LOGGER.info("Running main %s...", __version__)
    _LOGGER.warning("Running main %s...", __version__)


if __name__ == "__main__":
    _main()
