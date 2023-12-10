# Copyright (C) 2023 twyleg
import fileinput
import glob
import logging
import os
import shutil
from typing import Tuple

import yaml
import jsonschema
import json

from pathlib import Path

FILE_DIR = Path(__file__).parent


def load_config(config_path: Path) -> dict:
    with open(config_path, "r") as file:
        return yaml.safe_load(file)


def replace_string_in_file(filepath: Path, text_to_search: str, replacement_text: str):
    with fileinput.FileInput(filepath, inplace=True) as file:
        for line in file:
            print(line.replace(text_to_search, replacement_text), end="")


def update_files(placeholder: str, target: str, files: dict, dry_run=False) -> None:
    logging.info("Updating file:")
    if files is None:
        logging.info("  Nothing!")
    else:
        for file in files:
            logging.info("  %s: %s -> %s", file, placeholder, target)
            if not dry_run:
                replace_string_in_file(Path(file), placeholder, target)


def rename_files(target: str, files: dict, dry_run=False) -> None:
    logging.info("Renaming files:")
    if files is None:
        logging.info("  Nothing!")
    else:
        for rename_file in files:
            rename_file_path = Path(rename_file)
            new_file_path = rename_file_path.parent / (target + rename_file_path.suffix)
            logging.info("  %s -> %s", rename_file_path, new_file_path)
            if not dry_run:
                shutil.move(rename_file_path, new_file_path)


def rename_dirs(target: str, dirs: dict, dry_run=False) -> None:
    logging.info("Renaming dirs:")
    if dirs is None:
        logging.info("  Nothing!")
    else:
        for rename_dir in dirs:
            rename_dir_path = Path(rename_dir)
            new_dir_path = rename_dir_path.parent / target
            logging.info("  %s -> %s", rename_dir_path, new_dir_path)
            if not dry_run:
                shutil.move(rename_dir_path, new_dir_path)


def remove_files(files: dict, dry_run=False) -> None:
    logging.info("Removing files:")
    if files is None:
        logging.info("  Nothing!")
    else:
        for file in files:
            logging.info("  %s", file)
            if not dry_run:
                os.remove(file)


def remove_dirs(dirs: dict, dry_run=False) -> None:
    logging.info("Removing dirs:")
    if dirs is None:
        logging.info("  Nothing!")
    else:
        for dir_path in dirs:
            logging.info("  %s", dir_path)
            if not dry_run:
                shutil.rmtree(dir_path)


def scan_for_keywords(base_dir_path: Path, keywords: list) -> Tuple[int, int]:
    dir_name_count = 0
    file_content_count = 0

    for path in base_dir_path.rglob("*"):
        if path == base_dir_path / ".git":
            pass  # Ignore
        elif path.is_dir():
            for keyword in keywords:
                if keyword in str(path.relative_to(base_dir_path)):
                    dir_name_count += 1
                    logging.debug("Dir path containing keyword '%s': %s", keyword, path)
        elif path.is_file():
            try:
                content = path.read_text()
                for keyword in keywords:
                    count = content.count(keyword)
                    file_content_count += count
                    if count:
                        logging.debug("File containing keyword '%s': %s", keyword, path)
            except UnicodeDecodeError as e:
                pass
    return dir_name_count, file_content_count


def init_template(config_path: Path, target_name: str, dry_run=False):
    config = load_config(config_path)
    logging.debug("Config: %s", config)

    logging.info("Change directory: %s", config_path.parent)
    os.chdir(config_path.parent)

    with open(FILE_DIR / "schemas/config.json") as config_schema_file:
        config_schema = json.load(config_schema_file)
        jsonschema.validate(instance=config, schema=config_schema)

    placeholder = config["placeholder"]

    prerun_scan_results = scan_for_keywords(config_path.parent, [placeholder])

    update_files_dict = config["update_files"]
    update_files(placeholder, target_name, update_files_dict, dry_run)

    rename_files_dict = config["rename_files"]
    rename_files(target_name, rename_files_dict, dry_run)

    rename_dirs_dict = config["rename_dirs"]
    rename_dirs(target_name, rename_dirs_dict, dry_run)

    remove_files_dict = config["remove_files"]
    remove_files(remove_files_dict, dry_run)

    remove_dirs_dict = config["remove_dirs"]
    remove_dirs(remove_dirs_dict, dry_run)

    postrun_scan_results = scan_for_keywords(config_path.parent, [placeholder])

    logging.info("Scan results for keywords '%s'", placeholder)
    logging.info("Occurrences before initialization: dirs=%d, files=%d", *prerun_scan_results)
    logging.info("Occurrences after initialization:  dirs=%d, files=%d", *postrun_scan_results)
