from concurrent.futures import process
from pathlib import Path
import argparse
import re
import shlex
import sys
import importlib.metadata

from .path_scan import PathScanner
from .jobqueue import JobQueue
from .ffmpeg import FFMPEG_SUPPORTED_EXTENSIONS
from .ffmpeg_validator import FFMPEGValidateOperation
from .ffmpeg_transcoder import FFMPEG_PRESETS, FFMPEGTranscoderOperation
from .par2 import CreatePar2Operation, VerifyPar2Operation, DEFAULT_PAR2_CREATE_ARGS, DEFAULT_PAR2_VERIFY_ARGS
from .operation import Operation, PrintFilesOperation

"""
Default precious extensions that we want to preserve w/PAR2.
"""
DEFAULT_EXTENSIONS = ','.join(FFMPEG_SUPPORTED_EXTENSIONS + [
    # Docs
    "pdf",
    # Subtitles
    "srt", "idx", "sub",
    # Chiptunes
    "d64", "mod", "s3m"])
DEFAULT_IGNORE_FILES = ','.join([r"\.DS_Store", r"Thumbs\.db", r"\._.*", r".*\.par2", r".*\.filelist"])
DEFAULT_SPAM_FILES =','.join(["RARBG.txt", "RARBG_DO_NOT_MIRROR.exe", "WWW.YIFY-TORRENTS.COM.jpg", "www.YTS.AM.jpg", "WWW.YTS.TO.jpg", "www.YTS.LT.jpg"])

def process_dir(q: JobQueue, scanner: PathScanner, dir: Path, op: Operation):
    results = scanner.scan(q, dir)
    if results.unknown_extensions:
        q.warning(f"Unknown extensions found in path: {' '.join(results.unknown_extensions)}")
    if results.media_list:
        op.operate(q, dir, results.media_list)
    for dir in results.directory_list:
        q.submit(dir.name, lambda q: process_dir(q, scanner, dir, op))
    q.wait()

def compile_extension_regex(extensions):
    return re.compile('|'.join([f'\.{e}' for e in extensions.split(',')]), flags=re.IGNORECASE)

def compile_ignore_regex(files):
    return re.compile('|'.join([f'({f})' for f in files.split(',')]))

def do_main():
    try:
        __version__ = importlib.metadata.version(__package__ or __name__)
    except:
        __version__ = "(dev)"
    parser = argparse.ArgumentParser(description=f'automedia {__version__}: Process media directories to validate and add parity files')
    parser.add_argument("--hidden-container-prefix", dest="container_prefix", action="store", help=argparse.SUPPRESS)
    parser.add_argument("--hidden-container-pwd", dest="container_pwd", action="store", help=argparse.SUPPRESS)
    parser.add_argument("--root", required=True, dest="root_dir", action="store", help="root directory for media")
    parser.add_argument("--extensions", default=DEFAULT_EXTENSIONS, help=f"file extensions to include in processing (default {DEFAULT_EXTENSIONS})")
    parser.add_argument("--ignore", default=DEFAULT_IGNORE_FILES, help=f"file regular expressions to completely exclude in processing (default {DEFAULT_IGNORE_FILES})")
    commands = parser.add_subparsers(dest="command", required=True, help="sub-command help (use sub-command --help for more info)")
    verify_cmd = commands.add_parser("verify", help="verify media files are corruption-free with FFMPEG")
    transcode_cmd = commands.add_parser("transcode", help="transcode media files with FFMPEG")
    transcode_cmd.add_argument("--preset", required=True, choices=FFMPEG_PRESETS.keys(), help=f"output format preset (one of {' '.join(FFMPEG_PRESETS.keys())})")
    transcode_cmd.add_argument("--output", required=True, help=f"output directory")
    print_cmd = commands.add_parser("print", help="print all media files")
    par2_create_cmd = commands.add_parser("par2-create", help="create a PAR2 archive in each directory")
    par2_create_cmd.add_argument("--par2-args", default=DEFAULT_PAR2_CREATE_ARGS, help=f"arguments to pass to PAR2 (default {DEFAULT_PAR2_CREATE_ARGS})")
    par2_create_cmd.add_argument("--name", dest="par2_name", default="recovery", help="recovery filename (for .par2 and .filelist files)")
    par2_verify_cmd = commands.add_parser("par2-verify", help="verify the PAR2 archive in each directory")
    par2_verify_cmd.add_argument("--par2-args", default=DEFAULT_PAR2_VERIFY_ARGS, help=f"arguments to pass to PAR2 (default {DEFAULT_PAR2_VERIFY_ARGS})")
    par2_verify_cmd.add_argument("--name", dest="par2_name", default="recovery", help="recovery filename (for .par2 and .filelist files)")

    args = parser.parse_args()

    extension_regex = compile_extension_regex(args.extensions)
    ignore_regex = compile_ignore_regex(args.ignore)
    if args.command == 'verify':
        operation = FFMPEGValidateOperation()
    elif args.command == 'transcode':
        preset = FFMPEG_PRESETS[args.preset]
        operation = FFMPEGTranscoderOperation(Path(args.output), preset.args, preset.ext)
    elif args.command == 'print':
        operation = PrintFilesOperation()
    elif args.command == 'par2-create':
        operation = CreatePar2Operation(shlex.split(args.par2_args), args.par2_name)
    elif args.command == 'par2-verify':
        operation = VerifyPar2Operation(shlex.split(args.par2_args), args.par2_name)
    else:
        print("Unexpected operation")
        sys.exit(1)
    q = JobQueue()

    # Docker-awareness
    root = Path(args.root_dir)
    if args.container_prefix:
        pwd = Path(args.container_pwd)
        root = pwd / root
        for candidate in args.container_prefix.split(','):
            candidate = Path(candidate) / root.relative_to('/')
            if candidate.exists():
                root = candidate
                break

    if not root.is_dir():
        print(f"Root must be a directory: {root}")
        sys.exit(1)

    scanner = PathScanner(
        supported_extension_matcher=lambda p: p.suffix and extension_regex.fullmatch(p.suffix),
        ignored_pattern_matcher=lambda p: ignore_regex.fullmatch(p.name),
        spam_files_matcher=lambda _: False)

    # Allow the operation to initalize and log if needed
    operation.initialize(q, root)
    q.flush_logs()

    q.submit(None, lambda q: process_dir(q, scanner, root, operation))
    q.wait()

def main():
    try:
        do_main()
    except KeyboardInterrupt:
        print("Interrupted by user!")
