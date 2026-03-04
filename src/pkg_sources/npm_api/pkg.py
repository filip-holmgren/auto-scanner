from pkg_sources.pkg import Pkg
from pkg_sources.pkg_api import PkgAPI

class NpmPkg(Pkg):
    def __init__(self, name, scope, version, description, keywords, date, links, author, publisher):
        self.name = name
        self.scope = scope
        self.version = version
        self.description = description
        self.keywords = keywords
        self.date = date
        self.links = links
        self.author = author
        self.publisher = publisher
    
    def get_name(self):
        return self.name

    def get_version(self):
        return self.version        
    
    @staticmethod
    def from_json(data: dict, api: PkgAPI) -> "NpmPkg":
        pkg = NpmPkg(
            name=data.get("name"),
            scope=data.get("scope"),
            version=data.get("version"),
            description=data.get("description"),
            keywords=data.get("keywords", []),
            date=data.get("date"),
            links=data.get("links", {}),
            author=data.get("author"),
            publisher=data.get("publisher"),
        )

        if api.has_package(pkg):
            return None
    
        api.add_package(pkg)
        return pkg