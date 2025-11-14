from __future__ import annotations

from logging import getLogger

from click import command, option
from utilities.logging import basic_config

from test_remote_script import __version__

_LOGGER = getLogger(__name__)
print(__name__)  # # noqa: T201


@command()
@option("--asdf", is_flag=True, default=False, show_default=False)
def _main(*, asdf: bool) -> None:
    basic_config(obj=_LOGGER, hostname=True)
    _LOGGER.info("Running main %s...", __version__)
    _LOGGER.info("And....%s", asdf)
    _LOGGER.warning("Running main %s...", __version__)


if __name__ == "__main__":
    basic_config(obj=_LOGGER, hostname=True)
    _main()
