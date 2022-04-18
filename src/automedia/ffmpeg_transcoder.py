from dataclasses import dataclass
from pathlib import Path
from typing import List

from .ffmpeg import ffmpeg_supports
from .forward_progress import subprocess_forward_progress
from .operation import Operation

@dataclass
class FFMPEGPreset:
    ext: str
    args: List[str]

FFMPEG_TRANSCODE_BASE_ARGS = [
    '-xerror',
    '-v', 'error', 
    '-y',
    '-i', '-',
    '-vn']
FFMPEG_PRESETS = {
    'aac-64k': FFMPEGPreset(ext='m4a', args=['-c:a', 'aac', '-b:a', '64k', '-f', 'mp4']),
    'aac-128k': FFMPEGPreset(ext='m4a', args=['-c:a', 'aac', '-b:a', '128k', '-f', 'mp4']),
    'mp3-128k': FFMPEGPreset(ext='mp3', args=['-c:a', 'mp3', '-b:a', '128k', '-f', 'mp3']),
    'mp3-320k': FFMPEGPreset(ext='mp3', args=['-c:a', 'mp3', '-b:a', '320k', '-f', 'mp3']),
    'flac': FFMPEGPreset(ext='flac', args=['-c:a', 'flac', '-f', 'flac']),
}

class FFMPEGTranscoderOperation(Operation):
    def __init__(self, output_dir: Path, transcode_args: List[str], extension: str) -> None:
        self.output_dir = output_dir
        self.transcode_args = FFMPEG_TRANSCODE_BASE_ARGS + transcode_args
        self.extension = f'.{extension}'
        
    def initialize(self, q, dir):
        q.info(f"Transcoding files: ffmpeg {' '.join(self.transcode_args)} [output-file] < [input-file]")
        self.root = dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def operate(self, q, dir, files: List[Path]):
        for file in files:
            q.submit(file.name, lambda q: self._job(q, file))
        q.wait()

    def _job(self, q, file: Path):
        if ffmpeg_supports(file):
            q.info(f"Transcoding...")
            out = self.output_dir / file.with_suffix(self.extension).relative_to(self.root)
            out.parent.mkdir(parents=True, exist_ok=True)
            args = self.transcode_args + [str(out)]
            errors = subprocess_forward_progress(file, args, "ffmpeg")
            if errors:
                q.error(errors)
            q.info(f"Size: {file.stat().st_size // 1024}k -> {out.stat().st_size // 1024}k")
