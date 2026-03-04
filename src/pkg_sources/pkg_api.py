from pkg_sources.pkg import Pkg
from abc import ABC, abstractmethod
from sqlite3 import Connection, OperationalError
import tinykv

class PkgAPI(ABC):
    def __init__(self, conn: Connection):
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
    
    @abstractmethod
    def search_packages(self, query: str, limit: int = 100) -> list[Pkg]:
        pass
