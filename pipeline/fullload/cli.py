"""Command line:  fullload build [--data competition|quickstart|PATH] [--out PATH]"""
from __future__ import annotations

import argparse
from pathlib import Path

from .config import BUNDLE_PATH
from .export import build_bundle, write_bundle


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="fullload")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="compute the demo bundle")
    b.add_argument("--data", default=None, help="competition (default), quickstart, or a path to a public/ folder")
    b.add_argument("--out", type=Path, default=BUNDLE_PATH)
    args = ap.parse_args(argv)
    if args.cmd == "build":
        print(f"wrote {write_bundle(build_bundle(args.data), args.out)}")


if __name__ == "__main__":
    main()
