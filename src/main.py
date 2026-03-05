from pkg_sources.npm_api.pkg_api import NpmAPI
from pkg_sources.pypi_api.pkg_api import PypiAPI
from pkg_sources.pkg_api import PkgAPI
from pkg_sources.pkg_api import Pkg

from dotenv import load_dotenv
from time import sleep
import os
import sqlite3
import subprocess
import argparse

load_dotenv()
repo_dir = os.getenv("REPO_DIR")

if not repo_dir:
    raise RuntimeError("REPO_DIR not set in .env")


def list_of_strings(arg):
    return arg.split(",")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scan-only",
        action="store_true",
        help="Skip searching and only scan packages from DB",
    )
    parser.add_argument(
        "--packages",
        default=[],
        nargs="*",
        help="Packages to scan and process",
    )
    parser.add_argument(
        "--limit",
        default=10,
        type=int,
        help="Limit number of searched packages (ignored with --scan-only)",
    )
    parser.add_argument(
        "--database-path",
        default="./db/pkgs.db",
        type=str,
        help="Path to the database file",
    )
    parser.add_argument(
        "--registry", choices=["npm", "pypi"], help="Only process a specific registry"
    )

    args = parser.parse_args()

    DB_PATH = args.database_path
    conn = sqlite3.connect(DB_PATH, autocommit=True)

    pkgApis: list[PkgAPI] = []

    registry_map = {
        "npm": NpmAPI,
        "pypi": PypiAPI,
    }

    pkgApis: list[PkgAPI] = []

    if args.registry:
        print(f"Processing {args.registry} packages")
        pkgApis.append(registry_map[args.registry](conn))
    else:
        print("Processing all registries")
        for api in registry_map.values():
            pkgApis.append(api(conn))

    if not args.scan_only:
        search_and_store(pkgApis, args)

    scan_from_db(pkgApis)

    conn.close()


def search_and_store(pkgApis: list[PkgAPI], args: argparse.Namespace) -> None:
    packages = args.packages
    for api in pkgApis:
        api.search_packages(packages, args.limit)


def scan_from_db(pkgApis: list[PkgAPI]) -> None:
    for api in pkgApis:
        pkgs = api.get_packages()
        for pkg in pkgs:
            scan_package(pkg, api.table_name)


def scan_package(pkg: Pkg, pkgAPIName: str) -> None:
    name = pkg.get_name()
    version = pkg.get_version()

    print(f"Scanning: {name}, {version}")
    run_container(pkgAPIName, name, version)
    sleep(1)


def run_container(packager: str, package: str, version: str) -> None:
    try:
        subprocess.run(
            ["make", "run", "--", "--package", packager, package, version],
            cwd=repo_dir,
            check=True,
        )
    except:
        print(f"Failed to scan {package} {version} from {packager}")
        return


if __name__ == "__main__":
    main()
