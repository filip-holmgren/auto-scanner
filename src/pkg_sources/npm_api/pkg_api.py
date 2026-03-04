from pkg_sources.pkg_api import PkgAPI
from pkg_sources.pkg_api import Pkg
from pkg_sources.npm_api.pkg import NpmPkg

from sqlite3 import Connection
from time import sleep
import requests

class NpmAPI(PkgAPI):    
    def __init__(self, conn: Connection):
        self.table_name = "npm"
        super().__init__(conn)
    
    def search_packages(self, query: str, limit: int = 100):
        URL = "https://registry.npmjs.org/-/v1/search"
        params = {
            "text": query,
            "size": 100
        }

        while True:
            try:
                response = requests.get(URL, params=params)
                response.raise_for_status()

                data = response.json()

                packages: list[Pkg] = []
                for item in data.get("objects", []):
                    pkg = NpmPkg.from_json(item["package"])
                    packages.append(pkg)

                    if self.has_package(pkg) == False:
                        self.add_package(pkg)

                return packages
            except:
                print("Rate limited. Sleeping for 10 seconds")
                sleep(10)