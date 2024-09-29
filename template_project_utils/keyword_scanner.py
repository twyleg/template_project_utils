# Copyright (C) 2024 twyleg
import logging
from pathlib import Path
from typing import List, Dict


FILE_DIR = Path(__file__).parent

logm = logging.getLogger(__name__)


class KeywordScanner:
    class ScanResults:

        @classmethod
        def create_empty_keyword_count_dict(cls, keywords: List[str]) -> Dict[str, int]:
            return {keyword: 0 for keyword in keywords}

        def __init__(self, keywords: List[str]) -> None:
            self.file_name_count: Dict[str, int] = self.create_empty_keyword_count_dict(keywords)
            self.dir_name_count: Dict[str, int] = self.create_empty_keyword_count_dict(keywords)
            self.file_content_count: Dict[str, int] = self.create_empty_keyword_count_dict(keywords)

        def empty(self) -> bool:
            file_name_count = sum(list(self.file_name_count.values()))
            dir_name_count = sum(list(self.dir_name_count.values()))
            file_content_count = sum(list(self.file_content_count.values()))
            return file_name_count == 0 and dir_name_count == 0 and file_content_count == 0

        def log(self) -> None:
            logging.debug(" - File names:")
            for keyword, count in self.file_name_count.items():
                logging.debug("     %s : %d", keyword, count)
            logging.debug(" - Directory names:")
            for keyword, count in self.dir_name_count.items():
                logging.debug("     %s : %d", keyword, count)
            logging.debug(" - File contents:")
            for keyword, count in self.file_content_count.items():
                logging.debug("     %s : %d", keyword, count)

    def __init__(self, scan_base_dir_path: Path, keywords: List[str]):
        self.scan_base_dir_path = scan_base_dir_path
        self.keywords = keywords

    def scan(self) -> ScanResults:
        scan_results = KeywordScanner.ScanResults(self.keywords)

        for path in self.scan_base_dir_path.rglob("*"):
            if path.is_relative_to(self.scan_base_dir_path / ".git/"):
                pass  # Ignore
            elif path.is_relative_to(self.scan_base_dir_path / "venv/"):
                pass  # Ignore
            elif path.is_relative_to(self.scan_base_dir_path / "logs/"):
                pass  # Ignore
            elif path.is_dir():
                for keyword in self.keywords:
                    relative_path = path.relative_to(self.scan_base_dir_path)
                    if keyword in relative_path.name:
                        scan_results.dir_name_count[keyword] += 1
                        logm.debug("Dir path containing keyword '%s': %s", keyword, path)
            elif path.is_file():
                relative_path = path.relative_to(self.scan_base_dir_path)
                for keyword in self.keywords:
                    if keyword in relative_path.name:
                        scan_results.file_name_count[keyword] += 1
                        logm.debug("File path containing keyword '%s': %s", keyword, path)

                try:
                    content = path.read_text()
                    for keyword in self.keywords:
                        count = content.count(keyword)
                        scan_results.file_content_count[keyword] += count
                        if count:
                            logm.debug("File containing keyword '%s': %s", keyword, path)
                except UnicodeDecodeError as e:
                    pass
        return scan_results
