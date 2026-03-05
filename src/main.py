from pkg_sources.npm_api.pkg_api import NpmAPI
from pkg_sources.pypi_api.pkg_api import PypiAPI
from pkg_sources.pkg_api import PkgAPI
from pkg_sources.pkg_api import Pkg

from dotenv import load_dotenv
from time import sleep
import os
import sqlite3
import subprocess
import sys
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
        "--limit",
        default=10,
        type=int,
        help="Limit number of packages to search (ignored with --scan-only) (default: %(default)s)",
    )
    parser.add_argument(
        "--database-path",
        default="./db/pkgs.db",
        type=str,
        help="Path to the database file (default: %(default)s)",
    )
    parser.add_argument(
        "--packages",
        default=[],
        nargs="*",
        help="Packages to scan and process (requires --registry)",
    )
    parser.add_argument(
        "--registry", choices=["npm", "pypi"], help="Only process packages from a specific registry"
    )

    only_part_group = parser.add_mutually_exclusive_group()
    only_part_group.add_argument(
        "--fetch-only",
        action="store_true",
        help="Skip scanning package and only fetch packages (cannot be used with --scan-only)",
    )
    only_part_group.add_argument(
        "--scan-only",
        action="store_true",
        help="Skip fetching and only scan packages from DB (cannot be used with --fetch-only)",
    )

    args = parser.parse_args()

    if args.packages and not args.registry:
        parser.error("--packages and --registry must be used together")

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

    if not args.fetch_only:
        scan_from_db(pkgApis, args)

    conn.close()


def search_and_store(pkgApis: list[PkgAPI], args: argparse.Namespace) -> None:
    packages = args.packages
    for api in pkgApis:
        api.search_packages(packages, args.limit)


def scan_from_db(pkgApis: list[PkgAPI], args: argparse.Namespace) -> None:
    packages = args.packages
    for api in pkgApis:
        if len(packages) == 0:
            pkgs = api.get_packages()
            for pkg in pkgs:
                scan_package(pkg, api.table_name)
        else:
            for name in packages:
                pkg = api.get_package(name)
                if pkg is None:
                    continue

                scan_package(pkg, api.table_name)


def scan_package(pkg: Pkg, pkgAPIName: str) -> None:
    name = pkg.get_name()
    version = pkg.get_version()

    print(f"Scanning: {name}, {version}")
    run_container(pkgAPIName, name, version)
    try:
        sleep(2)
    except KeyboardInterrupt:
        print("\nCtrl+C detected. Exiting...")
        sys.exit(130)  # SIGINT


def run_container(packager: str, package: str, version: str) -> None:
    try:
        subprocess.run(
            ["make", "run", "--", "--package", packager, package, version],
            cwd=repo_dir,
            check=True,
        )
    except subprocess.CalledProcessError:
        print(f"Failed to scan {package} {version} from {packager}")
        return


if __name__ == "__main__":
    main()
