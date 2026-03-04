from abc import ABC, abstractmethod

class Pkg(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_version(self) ->str:
        pass
