from pkg_sources.pkg_api import PkgAPI
from pkg_sources.pkg_api import Pkg
from pkg_sources.npm_api.pkg import NpmPkg

from sqlite3 import Connection
from time import sleep
import requests


class NpmAPI(PkgAPI):
    DEFAULT_PACKAGES = ["express", "react", "mongodb", "vue", "astro"]

    def __init__(self, conn: Connection):
        self.table_name = "npm"
        super().__init__(conn)

    def _search_package(self, query: str, limit: int) -> None:
        URL = "https://registry.npmjs.org/-/v1/search"
        params = {"text": query, "size": limit}

        attempts = 0
        while attempts < 6:
            try:
                response = requests.get(URL, params=params)
                response.raise_for_status()

                data = response.json()

                for item in data.get("objects", []):
                    pkg = NpmPkg.from_json(item["package"])

                    if self.has_package(pkg) == False:
                        self.add_package(pkg)
                        self._log(
                            f"Scan found {pkg.get_name()} version {pkg.get_version()}"
                        )
                    else:
                        self._log(f"Already have {pkg.get_name()}")

                return

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
