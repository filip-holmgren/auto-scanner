from abc import ABC, abstractmethod


class Pkg(ABC):
    def __init__(self, name, version):
        self.name = name
        self.version = version

    def get_name(self) -> str:
        return self.name

    def get_version(self) -> str:
        return self.version
