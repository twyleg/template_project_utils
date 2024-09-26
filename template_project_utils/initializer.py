# Copyright (C) 2024 twyleg
import fileinput
import logging
import os
import shutil
import yaml
import jsonschema
import json
import template_project_utils.git as git
from typing import Tuple, Dict, List, Any
from InquirerPy import inquirer
from pathlib import Path


FILE_DIR = Path(__file__).parent


class ScanResults:

    @classmethod
    def create_empty_keyword_count_dict(cls, keywords: List[str]) -> Dict[str, int]:
        return {keyword: 0 for keyword in keywords}

    def __init__(self, keywords: List[str]) -> None:
        self.file_name_count: Dict[str, int] = self.create_empty_keyword_count_dict(keywords)
        self.dir_name_count: Dict[str, int] = self.create_empty_keyword_count_dict(keywords)
        self.file_content_count: Dict[str, int] = self.create_empty_keyword_count_dict(keywords)

    def empty(self) -> bool:
        return not (self.file_name_count or self.dir_name_count or self.file_content_count)


def load_config(config_path: Path) -> Dict[str, Any]:
    with open(config_path, "r") as file:
        return yaml.safe_load(file)


def replace_string_in_file(filepath: Path, text_to_search: str, replacement_text: str):
    with fileinput.FileInput(filepath, inplace=True) as file:
        for line in file:
            line.replace(text_to_search, replacement_text)


def update_files(placeholder_target_dict: Dict[str, str], files: List[str], dry_run=False) -> None:
    logging.info("Updating file:")
    if files is None:
        logging.info("  Nothing!")
    else:
        for file in files:
            for placeholder, target in placeholder_target_dict.items():
                logging.info("  %s: %s -> %s", file, placeholder, target)
                if not dry_run:
                    replace_string_in_file(Path(file), placeholder, target)


def rename_files(placeholder_target_dict: Dict[str, str], files: List[str], dry_run=False) -> None:
    logging.info("Renaming files:")
    if files is None:
        logging.info("  Nothing!")
    else:
        for rename_file in files:
            for placeholder, target in placeholder_target_dict.items():
                logging.debug("  Placeholder: \"%s\", Target: \"%s\"", placeholder, target)
                if placeholder in rename_file:
                    rename_file_path = Path(rename_file)
                    new_file_name = rename_file_path.name.replace(placeholder, target)
                    new_file_path = rename_file_path.parent / new_file_name
                    logging.info("  %s -> %s", rename_file_path, new_file_path)
                    if not dry_run:
                        shutil.move(rename_file_path, new_file_path)


def rename_dirs(placeholder_target_dict: Dict[str, str], dirs: List[str], dry_run=False) -> None:
    logging.info("Renaming dirs:")
    if dirs is None:
        logging.info("  Nothing!")
    else:
        for rename_dir in dirs:
            for placeholder, target in placeholder_target_dict.items():
                logging.debug("  Placeholder: \"%s\", Target: \"%s\"", placeholder, target)
                if placeholder in rename_dir:
                    rename_dir_path = Path(rename_dir)
                    new_dir_name = rename_dir_path.name.replace(placeholder, target)
                    new_dir_path = rename_dir_path.parent / new_dir_name
                    logging.info("  %s -> %s", rename_dir_path, new_dir_path)
                    if not dry_run:
                        shutil.move(rename_dir_path, new_dir_path)


def remove_files(files: List[str], dry_run=False) -> None:
    logging.info("Removing files:")
    if files is None:
        logging.info("  Nothing!")
    else:
        for file in files:
            logging.info("  %s", file)
            if not dry_run:
                os.remove(file)


def remove_dirs(dirs: List[str], dry_run=False) -> None:
    logging.info("Removing dirs:")
    if dirs is None:
        logging.info("  Nothing!")
    else:
        for dir_path in dirs:
            logging.info("  %s", dir_path)
            if not dry_run:
                shutil.rmtree(dir_path, ignore_errors=True)


def scan_for_keywords(base_dir_path: Path, keywords: List[str]) -> ScanResults:
    scan_results = ScanResults(keywords)

    for path in base_dir_path.rglob("*"):
        if path.is_relative_to(base_dir_path / ".git/"):
            pass  # Ignore
        elif path.is_relative_to(base_dir_path / "venv/"):
            pass  # Ignore
        elif path.is_dir():
            for keyword in keywords:
                relative_path = path.relative_to(base_dir_path)
                if keyword in relative_path.name:
                    scan_results.dir_name_count[keyword] += 1
                    logging.debug("Dir path containing keyword '%s': %s", keyword, path)
        elif path.is_file():
            relative_path = path.relative_to(base_dir_path)
            for keyword in keywords:
                if keyword in relative_path.name:
                    scan_results.file_name_count[keyword] += 1
                    logging.debug("File path containing keyword '%s': %s", keyword, path)

            try:
                content = path.read_text()
                for keyword in keywords:
                    count = content.count(keyword)
                    scan_results.file_content_count[keyword] += count
                    if count:
                        logging.debug("File containing keyword '%s': %s", keyword, path)
            except UnicodeDecodeError as e:
                pass
    return scan_results


def init_template(config_path: Path, placeholder_target_dict: Dict[str, str], dry_run=False) -> ScanResults:

    def read_placeholder_target_dict_from_user_input() -> Dict[str, str]:
        user_input_placeholder_target_dict: Dict[str, str] = {}
        for ph in placeholder:
            target = inquirer.text(
                message=f"Target name for \"{ph}\":"
            ).execute()
            user_input_placeholder_target_dict[ph] = target
        return user_input_placeholder_target_dict


    config = load_config(config_path)
    logging.debug("Config: %s", config)

    logging.info("Change directory: %s", config_path.parent)
    os.chdir(config_path.parent)

    with open(FILE_DIR / "schemas/config.json") as config_schema_file:
        config_schema = json.load(config_schema_file)
        jsonschema.validate(instance=config, schema=config_schema)

    placeholder = config["placeholder"]
    if len(placeholder_target_dict) == 0:
        placeholder_target_dict = read_placeholder_target_dict_from_user_input()

    prerun_scan_results = scan_for_keywords(config_path.parent, placeholder)

    update_files_dict = config["update_files"]
    update_files(placeholder_target_dict, update_files_dict, dry_run)

    rename_files_dict = config["rename_files"]
    rename_files(placeholder_target_dict, rename_files_dict, dry_run)

    rename_dirs_dict = config["rename_dirs"]
    rename_dirs(placeholder_target_dict, rename_dirs_dict, dry_run)

    remove_files_dict = config["remove_files"]
    remove_files(remove_files_dict, dry_run)

    remove_dirs_dict = config["remove_dirs"]
    remove_dirs(remove_dirs_dict, dry_run)

    postrun_scan_results = scan_for_keywords(config_path.parent, placeholder)

    logging.info("Scan results for keywords '%s'", placeholder)

    def log_results(scan_results: ScanResults) -> None:
        logging.info(" - File names:")
        for keyword, count in scan_results.file_name_count.items():
            logging.info("     %s : %d", keyword, count)
        logging.info(" - Directory names:")
        for keyword, count in scan_results.dir_name_count.items():
            logging.info("     %s : %d", keyword, count)
        logging.info(" - File contents:")
        for keyword, count in scan_results.file_content_count.items():
            logging.info("     %s : %d", keyword, count)

    logging.info("Occurrences before initialization:")
    log_results(prerun_scan_results)

    logging.info("Occurrences after initialization:")
    log_results(postrun_scan_results)

    git.remove_remote(config_path.parent, "origin")

    return postrun_scan_results
