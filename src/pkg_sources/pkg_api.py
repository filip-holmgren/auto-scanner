from pkg_sources.pkg import Pkg
from abc import ABC, abstractmethod
from sqlite3 import Connection, OperationalError
import tinykv

class PkgAPI(ABC):
    def __init__(self, conn: Connection):
        self.conn = conn
        self.init_db(conn)

    def init_db(self, conn: Connection) -> None:
        try:
            tinykv.create_schema(conn, table=self.table_name)
        except OperationalError as e:
            if "already exists" in str(e):
                pass  # schema already created, ignore
            else:
                raise

        self.kv = tinykv.TinyKV(conn, table=self.table_name)

    def add_package(self, pkg: Pkg) -> None:
        self.kv.set(pkg.get_name(), pkg.get_version())

    def has_package(self, pkg: Pkg) -> bool:
        try:
            return self.kv.get(pkg.get_name())
        except KeyError:
            return False

    def get_package(self, name: str) -> Pkg:
        return Pkg(name, self.kv.get(name))

    def get_packages(self) -> list[Pkg]:
        npmRows = self.conn.execute(f"SELECT k, v FROM {self.table_name}").fetchall()
        result = []
        for name, version in npmRows:
            result.append(Pkg(name, version))

        return result

    def search_packages(self, query: list[str], limit: int) -> list[Pkg]:
        actual_query = query

        if len(actual_query) == 0:
            actual_query = self.DEFAULT_PACKAGES
            self._log("No packages provided, using default.")

        for package in actual_query:
            self._log(f"Parsing package {package}")
            self._search_package(package, limit)

    def _log(self, *values: object) -> None:
        print(f"[{self.table_name}]", *values)

    @abstractmethod
    def _search_package(self, query: str, limit: int) -> None:
        pass
