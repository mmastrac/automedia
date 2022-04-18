import re

def compile_extension_regex(*extensions):
    return re.compile('|'.join([f'\.{e}' for e in extensions]), flags=re.IGNORECASE)

FFMPEG_SUPPORTED_EXTENSIONS = [
    # Video
    "mp4", "m4v", "mov", "avi", "mkv", "mpeg", "mpg",
    # Music
    "aac", "mp3", "flac", "ogg", "m4a", "wav", "wma",
    # Pics
    "jpg", "jpeg", "png", "gif"]
FFMPEG_SUPPORTED_EXTENSIONS_REGEX = compile_extension_regex(*FFMPEG_SUPPORTED_EXTENSIONS)

def ffmpeg_supports(filename):
    if FFMPEG_SUPPORTED_EXTENSIONS_REGEX.match(filename.suffix):
        return True
    return False
