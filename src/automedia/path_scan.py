import os

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from stat import S_ISDIR, S_ISREG
from typing import Callable, List

class EntryType(Enum):
    DIR = 0,
    FILE_MEDIA = 1,
    FILE_IGNORE = 2,
    FILE_SPAM = 3

@dataclass
class PathScanResults:
    directory_list: List[Path]
    media_list: List[Path]
    unknown_extensions: List[str]

class PathScanner:
    def __init__(self,
        supported_extension_matcher: Callable[[Path], bool] = None,
        ignored_pattern_matcher: Callable[[Path], bool] = None,
        spam_files_matcher: Callable[[Path], bool] = None) -> None:

        self.supported_extension_matcher = supported_extension_matcher
        self.ignored_pattern_matcher = ignored_pattern_matcher
        self.spam_files_matcher = spam_files_matcher

    def scan(self, q, dir):
        files = []
        dirs = []
        unknown_extensions = set()
        for f in os.listdir(dir):
            filename = dir / f
            if self.ignored_pattern_matcher(filename):
                continue
            try:
                st = os.lstat(filename)
            except Exception as e:
                q.error(f"Unrecoverable filesystem error while trying to read {f} ({e})")
                continue
            # Ignore zero-length files
            if st.st_size == 0:
                continue
            if S_ISREG(st.st_mode):
                if self.supported_extension_matcher(filename):
                    files.append(filename)
                else:
                    if filename.suffix:
                        unknown_extensions.add(filename.suffix)
            elif S_ISDIR(st.st_mode):
                dirs.append(filename)
            pass
        unknown_extensions = list(unknown_extensions)
        unknown_extensions.sort()
        files.sort()
        dirs.sort()

        return PathScanResults(directory_list=dirs, media_list=files, unknown_extensions=unknown_extensions)
