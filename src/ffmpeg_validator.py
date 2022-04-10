import os
import re

from .jobqueue import JobQueue
from .forward_progress import subprocess_forward_progress
from .operation import Operation

def compile_extension_regex(*extensions):
    return re.compile('|'.join([f'\.{e}' for e in extensions]), flags=re.IGNORECASE)

FFMPEG_SUPPORTED_EXTENSIONS = [
    # Video
    "mp4", "mov", "avi", "mkv", "srt", "mpeg", "mpg",
    # Music
    "aac", "mp3", "flac", "ogg", "m4a", "wav", "wma",
    # Pics
    "jpg", "jpeg", "png", "gif"]
FFMPEG_SUPPORTED_EXTENSIONS_REGEX = compile_extension_regex(*FFMPEG_SUPPORTED_EXTENSIONS)

class ClosedException(BaseException):
    pass

"""
We don't need the full complexity of the python streams, so let's work directly off OS file descriptors.
"""
class BasicStream:
    def __init__(self, fd) -> None:
        self.fd = fd
    def read(self, n):
        if self.fd == -1:
            raise ClosedException("Read on closed stream")
        return os.read(self.fd, n)
    def write(self, data):
        if self.fd == -1:
            raise ClosedException("Write on closed stream")
        return os.write(self.fd, data)
    def close(self):
        if self.fd != -1:
            try:
                os.close(self.fd)
            except OSError:
                pass
        self.fd = -1

def ffmpeg_supports(filename):
    if FFMPEG_SUPPORTED_EXTENSIONS_REGEX.match(filename.suffix):
        return True
    return False

def ffmpeg_validate(input, timeout=10, executable="ffmpeg", progress_callback=None):
    args = [
        "-xerror",
        "-v", "error",
        "-i", "-",
        "-f", "null",
        "-"
    ]

    return subprocess_forward_progress(input, args, executable, timeout=timeout, progress_callback=progress_callback)

class FFMPEGValidateOperation(Operation):
    def operate(self, q: JobQueue, dir, files):
        stats = { 'good': 0, 'bad': 0, 'ignored': 0 }
        for file in files:
            q.submit(file.name, lambda q: self._job(q, stats, file))
        q.wait()
        if stats['ignored']:
            q.info(f"{stats['good']} good file(s), {stats['bad']} bad file(s), {stats['ignored']} ignored file(s)")
        elif stats['bad']:
            q.info(f"{stats['good']} good file(s), {stats['bad']} bad file(s)")
        else:
            q.info(f"{stats['good']} good file(s)")

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

if __name__ == '__main__':
    import sys
    errors = ffmpeg_validate(sys.argv[1], timeout=1, executable="ffmpeg")
    if errors:
        print(errors)
    else:
        print("Ok!")
