from __future__ import annotations

from typing import TYPE_CHECKING

from pytest import mark, param

from installer.enums import Subnet
from installer.utilities import get_subnet, has_non_root, is_lxc, is_proxmox, run

if TYPE_CHECKING:
    from pathlib import Path


class TestGetSubnet:
    def test_main(self) -> None:
        subnet = get_subnet()
        assert isinstance(subnet, Subnet)
        assert isinstance(subnet.n, int)


class TestHasNonRoot:
    def test_main(self) -> None:
        assert isinstance(has_non_root(), bool)


class TestIsLXC:
    def test_main(self) -> None:
        assert isinstance(is_lxc(), bool)


class TestIsProxmox:
    def test_main(self) -> None:
        assert isinstance(is_proxmox(), bool)


class TestRun:
    def test_main(self) -> None:
        assert run("echo test") is None

    def test_output(self) -> None:
        assert run("echo test", output=True) == "test"

    @mark.parametrize(
        ("cmd", "expected"), [param("echo test", True), param("invalid-command", False)]
    )
    def test_failable(self, *, cmd: str, expected: bool) -> None:
        assert run(cmd, failable=True) is expected

    def test_output_and_failable(self) -> None:
        assert run("invalid-command", output=True, failable=True) is None

    def test_cwd(self, *, tmp_path: Path) -> None:
        assert run("pwd", output=True, cwd=tmp_path) == str(tmp_path)
