from pkg_sources.pkg import Pkg
from pkg_sources.pkg_api import PkgAPI

class NpmPkg(Pkg):
    @staticmethod
    def from_json(data: dict, api: PkgAPI) -> "NpmPkg":
        pkg = NpmPkg(
            name=data.get("name"),
            version=data.get("version")
        )
        
        return pkg