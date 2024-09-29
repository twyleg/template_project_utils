# Copyright (C) 2024 twyleg
import fileinput
import logging
import os
import shutil
import yaml
import jsonschema
import json
import template_project_utils.git as git
from typing import Dict, List, Any
from InquirerPy import inquirer
from pathlib import Path


FILE_DIR = Path(__file__).parent

logm = logging.getLogger(__name__)


class TemplateInitializer:

    def __init__(self, config_file_path: Path, working_dir_path: Path | None = None, dry_run=False):
        self.config_file_path = config_file_path
        self.working_dir_path = working_dir_path if working_dir_path else config_file_path.parent
        self.dry_run = dry_run

        self.config = self._load_config(self.config_file_path)
        logm.debug("Config: %s", self.config)

        with open(FILE_DIR / "resources/schemas/config.json") as config_schema_file:
            config_schema = json.load(config_schema_file)
            jsonschema.validate(instance=self.config, schema=config_schema)

        self.placeholder_target_dict: Dict[str, str | None] = {placeholder: None for placeholder in self.config["placeholder"]}
        self.files_to_update: List[str] | None = self.config["update_files"]
        self.files_to_rename: List[str] | None = self.config["rename_files"]
        self.dirs_to_rename: List[str] | None = self.config["rename_dirs"]
        self.files_to_remove: List[str] | None = self.config["remove_files"]
        self.dirs_to_remove: List[str] | None = self.config["remove_dirs"]

    @classmethod
    def _load_config(cls, config_path: Path) -> Dict[str, Any]:
        with open(config_path, "r") as file:
            return yaml.safe_load(file)

    @classmethod
    def replace_string_in_file(cls, filepath: Path, text_to_search: str, replacement_text: str):
        with fileinput.FileInput(filepath, inplace=True) as file:
            for line in file:
                line.replace(text_to_search, replacement_text)

    def _update_files(self) -> None:
        logm.info("Updating files:")
        if self.files_to_update is None:
            logm.info("  Nothing!")
        else:
            for file_to_update in self.files_to_update:
                for placeholder, target in self.placeholder_target_dict.items():
                    logm.info("  %s: %s -> %s", file_to_update, placeholder, target)
                    if not self.dry_run:
                        assert target
                        self.replace_string_in_file(Path(file_to_update), placeholder, target)

    def _rename_files(self) -> None:
        logm.info("Renaming files:")
        if self.files_to_rename is None:
            logm.info("  Nothing!")
        else:
            for file_to_rename in self.files_to_rename:
                for placeholder, target in self.placeholder_target_dict.items():
                    logm.debug('  Placeholder: "%s", Target: "%s"', placeholder, target)
                    if placeholder in file_to_rename:
                        assert target
                        rename_file_path = Path(file_to_rename)
                        new_file_name = rename_file_path.name.replace(placeholder, target)
                        new_file_path = rename_file_path.parent / new_file_name
                        logm.info("  %s -> %s", rename_file_path, new_file_path)
                        if not self.dry_run:
                            shutil.move(rename_file_path, new_file_path)

    def _rename_dirs(self) -> None:
        logm.info("Renaming dirs:")
        if self.dirs_to_rename is None:
            logm.info("  Nothing!")
        else:
            for dir_to_rename in self.dirs_to_rename:
                for placeholder, target in self.placeholder_target_dict.items():
                    logm.debug('  Placeholder: "%s", Target: "%s"', placeholder, target)
                    if placeholder in dir_to_rename:
                        assert target
                        rename_dir_path = Path(dir_to_rename)
                        new_dir_name = rename_dir_path.name.replace(placeholder, target)
                        new_dir_path = rename_dir_path.parent / new_dir_name
                        logm.info("  %s -> %s", rename_dir_path, new_dir_path)
                        if not self.dry_run:
                            shutil.move(rename_dir_path, new_dir_path)

    def _remove_files(self) -> None:
        logm.info("Removing files:")
        if self.files_to_remove is None:
            logm.info("  Nothing!")
        else:
            for file_to_remove in self.files_to_remove:
                logm.info("  %s", file_to_remove)
                if not self.dry_run:
                    os.remove(file_to_remove)

    def _remove_dirs(self) -> None:
        logm.info("Removing dirs:")
        if self.dirs_to_remove is None:
            logm.info("  Nothing!")
        else:
            for dir_to_remove in self.dirs_to_remove:
                logm.info("  %s", dir_to_remove)
                if not self.dry_run:
                    shutil.rmtree(dir_to_remove, ignore_errors=True)

    def init(self, placeholder_target_dict: Dict[str, str] = {}) -> None:

        def read_target_for_placeholder_from_user_input(placeholder: str) -> str:
            return inquirer.text(message=f'Target name for "{placeholder}":').execute()

        logm.info("Change directory: %s", self.working_dir_path)
        os.chdir(self.working_dir_path)

        for placeholder, target in self.placeholder_target_dict.items():
            if placeholder in placeholder_target_dict:
                target = placeholder_target_dict[placeholder]
                self.placeholder_target_dict[placeholder] = target
                logm.info('Target name from arguments for "%s": "%s"', placeholder, target)
            else:
                target = read_target_for_placeholder_from_user_input(placeholder)
                self.placeholder_target_dict[placeholder] = target
                logm.info('Target name from user input for "%s": "%s"', placeholder, target)

        self._update_files()
        self._rename_files()
        self._rename_dirs()
        self._remove_files()
        self._remove_dirs()

        git.remove_remote(self.working_dir_path, "origin")
