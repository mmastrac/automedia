from abc import abstractmethod
from pathlib import Path
from stat import *
import argparse
import glob
import os
import re

from .jobqueue import JobQueue
from .ffmpeg_validator import ffmpeg_supports, ffmpeg_validate

DEFAULT_EXTENSIONS = ','.join([
    # Video
    "mp4", "mov", "avi", "mkv", "srt",
    # Music
    "aac", "mp3", "flac", "ogg", "m4a",
    # Pics
    "jpg", "png", "gif",
    # Docs
    "pdf",
    # Chiptunes
    "d64", "mod", "s3m"])
DEFAULT_IGNORE_FILES = ','.join([r"\.DS_Store", "Thumbs\.db", "\._.*"])
DEFAULT_SPAM_FILES =','.join(["RARBG.txt", "RARBG_DO_NOT_MIRROR.exe", "WWW.YIFY-TORRENTS.COM.jpg", "www.YTS.AM.jpg", "WWW.YTS.TO.jpg", "www.YTS.LT.jpg"])

class Operation:
    @abstractmethod
    def operate(dir, files):
        pass

class CreatePar2:
    pass

class FFMPEGValidate:
    def operate(self, q, dir, files):
        stats = { 'good': 0, 'bad': 0, 'ignored': 0 }
        for file in files:
            q.submit(file, lambda q: self._job(q, stats, dir / file))
        q.wait()
        q.info(f"{stats['good']} good file(s), {stats['bad']} bad file(s), {stats['ignored']} ignored file(s)")
        pass

    def _job(self, q, stats, file):
        if ffmpeg_supports(file):
            errors = ffmpeg_validate(file)
            if errors:
                stats['bad'] += 1
                q.error(errors)
            else:
                stats['good'] += 1
        else:
            stats['ignored'] += 1

class PrintFilesOperation:
    def operate(self, q, dir, files):
        q.info(f"{len(files)} file(s)")
        for file in files:
            q.info(f"  {file}")
        pass

def process_dir(q: JobQueue, extension_regex: re.Pattern, ignore_regex: re.Pattern, dir: Path, op: Operation):
    files = []
    unknown_extensions = set()
    for f in os.listdir(dir):
        if ignore_regex.fullmatch(f):
            continue
        filename = dir / f
        st = os.lstat(filename)
        # Ignore zero-length files
        if st.st_size == 0:
            continue
        if S_ISREG(st.st_mode):
            fullext = filename.suffix
            if fullext:
                if extension_regex.fullmatch(fullext):
                    files.append(f)
                else:
                    unknown_extensions.add(fullext)
        pass
    if unknown_extensions:
        l = list(unknown_extensions)
        l.sort()
        q.warning(f"Unknown extensions found in path: {' '.join(l)}")
    if files:
        files.sort()
        op.operate(q, dir, files)

def compile_extension_regex(extensions):
    return re.compile('|'.join([f'\.{e}' for e in extensions.split(',')]), flags=re.IGNORECASE)

def compile_ignore_regex(files):
    return re.compile('|'.join([f'({f})' for f in files.split(',')]))

def main():
    parser = argparse.ArgumentParser(description='Process media directories to validate and add parity files')
    parser.add_argument("--root", required=True, dest="root_dir", action="store", help="root directory for media")
    parser.add_argument("--hidden-container-prefix", dest="container_prefix", action="store", help=argparse.SUPPRESS)
    parser.add_argument("--extensions", default=DEFAULT_EXTENSIONS, help=f"file extensions to include in processing (default {DEFAULT_EXTENSIONS})")
    parser.add_argument("--ignore", default=DEFAULT_IGNORE_FILES, help=f"file regular expressions to completely exclude in processing (default {DEFAULT_IGNORE_FILES})")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--verify", action="store_true", help="Verify media files are corruption-free with FFMPEG")
    mode.add_argument("--print", action="store_true", help="Print all media files")
    args = parser.parse_args()

    extension_regex = compile_extension_regex(args.extensions)
    ignore_regex = compile_ignore_regex(args.ignore)
    if args.verify:
        operation = FFMPEGValidate()
    if args.print:
        operation = PrintFilesOperation()
    q = JobQueue()

    # Walk everything from the root dir, but only care about directories
    root = Path(args.root_dir)
    if args.container_prefix:
        for candidate in args.container_prefix.split(','):
            candidate = Path(candidate) / root.relative_to('/')
            if candidate.exists():
                root = candidate
                break

    for filename in glob.iglob(str(root / '**'), recursive=True):
        st = os.lstat(filename)
        if S_ISDIR(st.st_mode):
            dir = Path(filename)
            q.submit(dir.relative_to(root), lambda q: process_dir(q, extension_regex, ignore_regex, dir, operation))

    q.wait()

try:
    main()
except KeyboardInterrupt:
    print("Interrupted by user!")
