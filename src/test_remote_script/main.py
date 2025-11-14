from __future__ import annotations

from logging import getLogger

from click import command, option
from utilities.click import CONTEXT_SETTINGS_HELP_OPTION_NAMES
from utilities.logging import basic_config

from test_remote_script import __version__

_LOGGER = getLogger(__name__)


@command(**CONTEXT_SETTINGS_HELP_OPTION_NAMES)
@option("--asdf", is_flag=True, default=False, show_default=False)
def _main(*, asdf: bool) -> None:
    _LOGGER.info("Running main %s...", __version__)
    _LOGGER.info("And....%s", asdf)


if __name__ == "__main__":
    basic_config(obj=_LOGGER, hostname=True)
    _main()
