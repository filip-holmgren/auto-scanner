import requests
from pkg_sources.pkg_api import PkgAPI
from pkg_sources.pkg_api import Pkg
from pkg_sources.npm_api.pkg import NpmPkg

from sqlite3 import Connection, OperationalError
import tinykv

class NpmAPI(PkgAPI):    
    def __init__(self, conn: Connection):
        self.table_name = "npm"
        super().__init__(conn)
    
    def init_db(self, conn: Connection) -> None:
        try:
            tinykv.create_schema(conn, table=self.table_name)
        except OperationalError as e:
            if "already exists" in str(e):
                pass  # schema already created, ignore
            else:
                raise
        
        self.kv = tinykv.TinyKV(conn, table=self.table_name)
    
    def search_packages(self, query: str) -> list[Pkg]:
        URL = "https://registry.npmjs.org/-/v1/search"
        params = {
            "text": query,
            "size": 100
        }

        response = requests.get(URL, params=params)
        response.raise_for_status()

        data = response.json()

        packages = [
            pkg
            for item in data.get("objects", [])
            if (pkg := NpmPkg.from_json(item["package"], self)) is not None
        ]

        return packages

    def add_package(self, pkg: Pkg) -> None:
        self.kv.set(pkg.get_name(), pkg.get_version())
    
    def has_package(self, pkg: Pkg) -> bool:
        try:
            return self.kv.get(pkg.get_name()) == pkg.get_version()
        except KeyError:
            return False
