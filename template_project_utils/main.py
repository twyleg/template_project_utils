# Copyright (C) 2023 twyleg
import sys
import argparse
import logging

from pathlib import Path
from template_project_utils import __version__
from template_project_utils.initializer import init_template

FORMAT = "[%(asctime)s][%(levelname)s][%(name)s]: %(message)s"

FILE_DIR = Path(__file__).parent


def main() -> None:
    parser = argparse.ArgumentParser(usage="template_project_utils <command> [<args>] <files>")

    parser.add_argument("target_name", metavar="target_name", type=str, help="Name of the target project")

    parser.add_argument(
        "-v",
        "--version",
        help="Show version and exit",
        action="version",
        version=__version__,
    )

    parser.add_argument(
        "-vv",
        "--verbose",
        action="store_true",
        help="Show verbose output on stdout.",
    )

    parser.add_argument(
        "-d",
        "--dry",
        action="store_true",
        help="Run without actually modifying files.",
    )

    parser.add_argument(
        "-c",
        "--config",
        dest="config_file_path",
        default=Path.cwd() / "template_config.yaml",
        help='Config file to use. Default="./template_config.yaml"',
    )

    args = parser.parse_args()

    logging.basicConfig(stream=sys.stdout, format=FORMAT, level=logging.DEBUG if args.verbose else logging.INFO)
    logging.info("template_project_utils started!")

    init_template(args.config_file_path, args.target_name, args.dry)


if __name__ == "__main__":
    main()
