from pkg_sources.pkg_api import PkgAPI
from pkg_sources.pkg_api import Pkg
from pkg_sources.pypi_api.pkg import PypiPkg

from sqlite3 import Connection
import requests

class PypiAPI(PkgAPI):    
    def __init__(self, conn: Connection):
        self.table_name = "pypi"
        super().__init__(conn)
    
    def search_packages(self, query: str, limit: int = 100) -> list[Pkg]:
        URL = "https://pypi.org/simple"
        HEADERS = {
            "Accept": "application/vnd.pypi.simple.v1+json"
        }

        print("Fetching pypi projects")
        response = requests.get(URL, headers=HEADERS)
        response.raise_for_status()

        data = response.json()
        projects = data.get("projects", [])
        names = [p["name"] for p in projects]

        packages: list[Pkg] = []

        gotten = 0
        for name in names:
            print(f"Scanning {name}")
            version = self._get_version(name)
            if version is None:
                print(f"Couldn't find version for {name}")
                continue
            
            pkg = PypiPkg.from_data(name, version, self)
            if self.has_package(pkg) == False:
                self.add_package(pkg)
                print(f"Scan found {name} version {version}")
            else:
                print(f"Already have {name}")

            packages.append(pkg)
            gotten = gotten + 1
            
            if gotten >= limit:
                print("Limit reached, exiting")
                break

        return packages

    def _get_version(self, name: str) -> str | None:
        url = f"https://pypi.org/pypi/{name}/json"
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            
            return resp.json()["info"]["version"]
        except:
            return None