from __future__ import annotations

from subprocess import check_call

from utilities.pathlib import get_repo_root
from utilities.pytest import throttle
from utilities.tempfile import TemporaryDirectory
from utilities.whenever import MINUTE


class TestCLI:
    @throttle(delta=MINUTE)
    def test_entrypoint(self) -> None:
        root = get_repo_root()
        with TemporaryDirectory() as temp_dir:
            _ = check_call(
                f"./entrypoint.py --repo-path={temp_dir}", shell=True, cwd=root
            )

    @throttle(delta=MINUTE)
    def test_main(self) -> None:
        root = get_repo_root()
        _ = check_call("python3 -m installer.main --help", shell=True, cwd=root)
