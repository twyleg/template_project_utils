# Copyright (C) 2024 twyleg
import argparse
import re
from pathlib import Path
from typing import Dict

from simple_python_app.generic_application import GenericApplication

from template_project_utils import __version__
from template_project_utils.keyword_scanner import KeywordScanner
from template_project_utils.template_initializer import TemplateInitializer


FILE_DIR = Path(__file__).parent


class TemplateProjectUtils(GenericApplication):

    def __init__(self):
        # fmt: off
        super().__init__(
            application_name="template_project_utils",
            version=__version__,
            application_config_init_enabled=False,
            logging_init_custom_logging_enabled=False,
            logging_default_config_filepath=FILE_DIR / "resources/configs/default_logging_config.yaml",
            logging_logfile_output_dir=Path.cwd() / "logs"
        )
        # fmt: on

    def add_arguments(self, argparser: argparse.ArgumentParser):
        argparser.add_argument(
            "-d",
            "--dry",
            action="store_true",
            help="Run without actually modifying files.",
        )

        def regex_type(pattern: str | re.Pattern):
            """Argument type for matching a regex pattern."""

            def closure_check_regex(arg_value):
                if not re.match(pattern, arg_value):
                    raise argparse.ArgumentTypeError("invalid value")
                return arg_value

            return closure_check_regex

        argparser.add_argument(
            "placeholder_target",
            metavar="placeholder_target",
            type=regex_type(r"^[^=]+=[^=]+$"),
            nargs="*",
            help="Placeholder target pair (placeholder=target).",
        )

    def _get_placeholder_target_pairs_from_arguments(self, args: argparse.Namespace) -> Dict[str, str]:
        placeholder_target_dict: Dict[str, str] = {}
        for placeholder_target in args.placeholder_target:
            placeholder, target = placeholder_target.split("=")
            placeholder_target_dict[placeholder] = target
        return placeholder_target_dict

    def run(self, args: argparse.Namespace) -> int:
        config_file_path = Path(args.config) if args.config else Path.cwd() / "template_config.yaml"
        template_initializer = TemplateInitializer(config_file_path, dry_run=args.dry)

        placeholder_keywords = list(template_initializer.placeholder_target_dict.keys())
        placeholder_keyword_scanner = KeywordScanner(scan_base_dir_path=config_file_path.parent, keywords=placeholder_keywords)

        placeholder_target_dict = self._get_placeholder_target_pairs_from_arguments(args)
        self.logm.debug("Placeholder Target pairs from arguments: %s", placeholder_target_dict)

        prerun_scan_results = placeholder_keyword_scanner.scan()
        template_initializer.init(placeholder_target_dict)
        postrun_scan_results = placeholder_keyword_scanner.scan()

        self.logm.debug("Placeholder keyword pre init run:")
        prerun_scan_results.log()
        self.logm.debug("Placeholder keyword post init run:")
        postrun_scan_results.log()

        if postrun_scan_results.empty():
            self.logm.info("Project initialized successfully!")
            return 0
        else:
            self.logm.error("Project initialization failed!")
            return -1


def main():
    template_project_utils = TemplateProjectUtils()
    template_project_utils.start()


if __name__ == "__main__":
    main()
