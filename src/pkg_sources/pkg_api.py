from pkg_sources.pkg import Pkg
from abc import ABC, abstractmethod
from sqlite3 import Connection

class PkgAPI(ABC):
    def __init__(self, conn: Connection):
        self.init_db(conn)

    @abstractmethod
    def init_db(self, conn: Connection) -> None:
        pass
    
    @abstractmethod
    def search_packages(self, query: str) -> list[Pkg]:
        pass

    @abstractmethod
    def add_package(self, pkg: Pkg) -> None:
        pass

    @abstractmethod
    def has_package(self, pkg: Pkg) -> bool:
        pass