from .ffmpeg import ffmpeg_supports
from .jobqueue import JobQueue
from .forward_progress import subprocess_forward_progress
from .operation import Operation

FFMPEG_VERIFY_ARGS = [
        "-xerror",
        "-v", "error",
        "-i", "-",
        "-f", "null",
        "-"
    ]

def ffmpeg_validate(input, timeout=10, executable="ffmpeg", progress_callback=None):
    return subprocess_forward_progress(input, FFMPEG_VERIFY_ARGS, executable, timeout=timeout, progress_callback=progress_callback)

class FFMPEGValidateOperation(Operation):
    def initialize(self, q, dir):
        q.info(f"Verifying internal consistency of media files: ffmpeg {' '.join(FFMPEG_VERIFY_ARGS)} < [file] > /dev/null")

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
