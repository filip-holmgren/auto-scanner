from pkg_sources.pkg import Pkg
from pkg_sources.pkg_api import PkgAPI


class PypiPkg(Pkg):
    @staticmethod
    def from_data(name: str, version: str) -> "PypiPkg":
        pkg = PypiPkg(name=name, version=version)

        return pkg
