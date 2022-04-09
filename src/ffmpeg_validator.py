import os
import time
import re
import subprocess
from subprocess import Popen, TimeoutExpired
from threading import Thread

def compile_extension_regex(*extensions):
    return re.compile('|'.join([f'\.{e}' for e in extensions]), flags=re.IGNORECASE)

BUFFER_SIZE = 128 * 1024
SUPPORTED_EXTENSIONS = compile_extension_regex(
    # Video
    "mp4", "mov", "avi", "mkv",
    # Music
    "aac", "mp3", "flac", "ogg", "m4a",
    # Pics
    "jpg", "png", "gif")

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
    if SUPPORTED_EXTENSIONS.match(filename.suffix):
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

    process = Popen(args=args, executable=executable, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    stdin = BasicStream(process.stdin.fileno())
    stderr = BasicStream(process.stderr.fileno())
    errors = []

    stderr_buffer = [b'']
    def stderr_reader(stderr, stderr_buffer):
        try:
            while True:
                r = stderr.read(128)
                stderr_buffer[0] += r
        except ClosedException:
            pass
        except:
            stderr.close()
    t1 = Thread(target=stderr_reader, args=(stderr, stderr_buffer,))
    t1.start()

    last_write = [time.monotonic()]
    progress = [0]
    def stdin_writer(stdin, progress, last_write):
        try:
            with open(input, 'rb') as f:
                fl = f.seek(0, 2)
                f.tell()
                f.seek(0, 0)
                w = 0
                while True:
                    bytes = f.read(BUFFER_SIZE)
                    if not bytes:
                        break
                    w += len(bytes)
                    stdin.write(bytes)
                    last_write[0] = time.monotonic()
                    progress[0] = w / fl
        except BrokenPipeError:
            errors.append("Process failed to read the entire input")
        except ClosedException:
            pass
        finally:
            stdin.close()
    t2 = Thread(target=stdin_writer, args=(stdin, progress, last_write,))
    t2.start()

    try:
        while True:
            if progress_callback:
                try:
                    progress_callback(progress[0])
                except:
                    pass
            if time.monotonic() - last_write[0] > timeout:
                errors.append("Process timed out reading from input stream")
                break
            if t1:
                t1.join(timeout=0)
                if not t1.is_alive():
                    t1 = None
            if t2:
                t2.join(timeout=0)
                if not t2.is_alive():
                    t2 = None
            try:
                ret = process.wait(timeout=0.01)
                if ret != 0:
                    errors.append(f"Process failed with exit code {ret}")
                break
            except TimeoutExpired:
                pass
            except KeyboardInterrupt as e:
                errors.append("Interrupted by user")
                raise e
            except:
                errors.append("Failed for unknown reason")
                break
    finally:
        stdin.close()
        stderr.close()
        Thread(target=lambda: process.kill()).start()
        if t1:
            t1.join()
        if t2:
            t2.join()
        if len(stderr_buffer[0]) > 0:
            errors.append("Process wrote to error stream: " + str(stderr_buffer[0], encoding='utf8', errors='replace'))
        if progress_callback:
            try:
                progress_callback(progress[1])
            except:
                pass

    return errors

if __name__ == '__main__':
    import sys
    errors = ffmpeg_validate(sys.argv[1], timeout=1, executable="ffmpeg")
    if errors:
        print(errors)
    else:
        print("Ok!")
