from pkg_sources.npm_api.pkg_api import NpmAPI
from pkg_sources.npm_api.pkg import NpmPkg
from pkg_sources.pkg_api import PkgAPI

import sqlite3

def main():
    DB_PATH = "./db/pkgs.db"
    conn = sqlite3.connect(DB_PATH, autocommit=True)
    
    apis: list[PkgAPI] = [
        NpmAPI(conn)
    ]
    
    for api in apis:
        packages: list[NpmPkg] = api.search_packages("express")

        for pkg in packages:
            print(pkg.get_name(), pkg.get_version())

    conn.close()

if __name__ == "__main__":
    main()
