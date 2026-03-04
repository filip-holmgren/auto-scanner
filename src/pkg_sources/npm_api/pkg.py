from pkg_sources.pkg import Pkg
from pkg_sources.pkg_api import PkgAPI

class NpmPkg(Pkg):
    def __init__(self, name, version):
        self.name = name
        self.version = version
    
    def get_name(self):
        return self.name

    def get_version(self):
        return self.version
    
    @staticmethod
    def from_json(data: dict, api: PkgAPI) -> "NpmPkg":
        pkg = NpmPkg(
            name=data.get("name"),
            version=data.get("version")
        )

        if api.has_package(pkg):
            return None
    
        api.add_package(pkg)
        return pkg