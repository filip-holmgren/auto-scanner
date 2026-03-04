from pkg_sources.pkg_api import PkgAPI
from pkg_sources.pkg_api import Pkg
from pkg_sources.npm_api.pkg import NpmPkg

from sqlite3 import Connection, OperationalError
import requests
import tinykv

class NpmAPI(PkgAPI):    
    def __init__(self, conn: Connection):
        self.table_name = "npm"
        super().__init__(conn)
    
    def search_packages(self, query: str, limit: int = 100) -> list[Pkg]:
        URL = "https://registry.npmjs.org/-/v1/search"
        params = {
            "text": query,
            "size": 100
        }

        response = requests.get(URL, params=params)
        response.raise_for_status()

        data = response.json()

        packages: list[Pkg] = []
        for item in data.get("objects", []):
            pkg = NpmPkg.from_json(item["package"], self)
            if pkg is not None:
                packages.append(pkg)

        return packages