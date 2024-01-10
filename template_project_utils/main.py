# Copyright (C) 2023 twyleg
import sys
import argparse
import logging

from pathlib import Path
from template_project_utils import __version__
from template_project_utils.initializer import init_template

FORMAT = "[%(asctime)s][%(levelname)s][%(name)s]: %(message)s"

FILE_DIR = Path(__file__).parent


def init(args: argparse.Namespace):
    init_template(args.config_file_path, args.target_name, args.dry)


def create(args: argparse.Namespace):
    logging.warning("Not yet implemented!")
    logging.warning("Will create project type='%s', branch='%s', name='%s'", args.type, args.branch, args.target_name)


def main() -> None:
    parser = argparse.ArgumentParser(usage="template_project_utils <command> [<args>] <files>")

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

    subparsers = parser.add_subparsers(required=True, title="subcommands")

    #
    # Subcommand: init
    #
    parser_init = subparsers.add_parser("init", description="Initialize a project.")
    parser_init.set_defaults(func=init)

    parser_init.add_argument("target_name", metavar="target_name", type=str, help="Name of the target project")

    #
    # Subcommand: create
    #
    parser_create = subparsers.add_parser("create", description="Create a new project based on a template.")
    parser_create.set_defaults(func=create)

    parser_create.add_argument(
        "-t",
        "--type",
        choices=["cpp", "python", "kicad"],
        type=str,
        nargs=1,
        required=True,
        help="Project type.",
    )

    parser_create.add_argument(
        "-b",
        "--branch",
        type=str,
        nargs=1,
        default="master",
        help="Git branch of template project to use (default='master').",
    )

    parser_create.add_argument("target_name", metavar="target_name", type=str, help="Name of the target project to create.")

    #
    # Subcommands end
    #
    args = parser.parse_args(sys.argv[1:])

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(stream=sys.stdout, format=FORMAT, level=log_level)
    logging.info("template_project_utils started!")
    logging.info("Log level: %s", logging.getLevelName(log_level))
    logging.info("Command: %s", args.func.__name__.replace("_", " -> "))
    logging.debug("Arguments: %s", args)

    args.func(args)


if __name__ == "__main__":
    main()
