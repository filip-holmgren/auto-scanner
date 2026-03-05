from pkg_sources.pkg_api import PkgAPI
from pkg_sources.pkg_api import Pkg
from pkg_sources.pypi_api.pkg import PypiPkg

from sqlite3 import Connection
from time import sleep
import requests


class PypiAPI(PkgAPI):
    DEFAULT_PACKAGES = ["fastapi", "httpx", "Flask"]

    def __init__(self, conn: Connection):
        self.table_name = "pypi"
        super().__init__(conn)

    def _search_package(self, query: str, limit: int) -> None:
        version = self._get_version(query)
        if version is None:
            self._log(f"Couldn't find version for {query}")
            return

        pkg = PypiPkg.from_data(query, version)
        if self.has_package(pkg) == False:
            self.add_package(pkg)
            self._log(f"Scan found {query} version {version}")
        else:
            self._log(f"Already have {query}")

    def _get_version(self, name: str) -> str | None:
        URL = f"https://pypi.org/pypi/{name}/json"
        attempts = 0
        while attempts < 6:
            try:
                response = requests.get(URL)
                response.raise_for_status()

                return response.json()["info"]["version"]
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")

                    if retry_after and int(retry_after) != 0:
                        sleep_time = int(retry_after)
                    else:
                        sleep_time = 2**attempts

                    self._log(f"Rate limited. Sleeping for {sleep_time} seconds")
                    sleep(sleep_time)
                    attempts += 1
                    continue

                # Unknown http error. Exit
                raise

            except Exception as e:
                self._log(f"Unexpected error: {e}")
                sleep(2**attempts)
                attempts += 1
