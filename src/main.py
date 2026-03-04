from pkg_sources.npm_api.pkg_api import NpmAPI
from pkg_sources.pypi_api.pkg_api import PypiAPI
from pkg_sources.pkg_api import Pkg
from dotenv import load_dotenv

import os
import sqlite3
import subprocess
import argparse

load_dotenv()
repo_dir = os.getenv("REPO_DIR")

if (not repo_dir):
    raise RuntimeError("REPO_DIR not set in .env")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan-only", action="store_true",
                        help="Skip searching and only scan packages from DB")
    args = parser.parse_args()
    
    DB_PATH = "./db/pkgs.db"
    conn = sqlite3.connect(DB_PATH, autocommit=True)

    if not args.scan_only:
        search_and_store(conn)

    scan_from_db(conn)

    conn.close()

def search_and_store(conn: sqlite3.Connection) -> None:
    PACKAGES = [
        # "express",
        "all.db",
        "expo-server",
        "webdriver-bidi-protocol",
        "telecom-mas-agent",
        "nexus-rpc",
        "ansi-styles",
        "debug",
        "semver",
        "supports-color",
        "chalk",
        "strip-ansi",
        "ms",
        "minimatch",
        "tslib",
        "brace-expansion",
        "pretty-format",
        "path-exists",
        "mime-db",
        "cross-spawn",
        "react",
        "mongodb",
        "vue",
        "astro"
    ]
    
    npmAPI = NpmAPI(conn)
    for pkgName in PACKAGES:
        print(f"Searching npm for {pkgName}")
        npmAPI.search_packages(pkgName, 10)

    pypiAPI = PypiAPI(conn)
    pypiAPI.search_packages("", 10)

def scan_from_db(conn: sqlite3.Connection) -> None:
    npmRows = conn.execute("SELECT k, v FROM npm").fetchall()
    pypiRows = conn.execute("SELECT k, v FROM pypi").fetchall()

    for name, version in npmRows:
        scan_package(Pkg(name, version))

    for name, version in pypiRows:
        scan_package(Pkg(name, version))

def scan_package(pkg: Pkg) -> None:
    name = pkg.get_name()
    version = pkg.get_version()

    print(f"Scanning: {name}, {version}")
    run_container("npm", name, version)

def run_container(packager: str, package: str, version: str) -> None:
    try:
        subprocess.run([
            "make", "run", "--",
            "--package", packager, package, version
        ], cwd=repo_dir, check=True)
    except:
        print(f"Failed to scan {package} {version} from {packager}")
        return

if __name__ == "__main__":
    main()
