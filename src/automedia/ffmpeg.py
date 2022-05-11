from dataclasses import dataclass
from enum import Enum
import re

class MediaType(Enum):
    Video = 0,
    Audio = 1,
    Image = 2,

def compile_extension_regex(*extensions):
    return re.compile('|'.join([f'\\.{e}' for e in extensions]), flags=re.IGNORECASE)

FFMPEG_SUPPORTED_EXTENSIONS_BY_TYPE = {
    MediaType.Video: ["mp4", "m4v", "mov", "avi", "mkv", "mpeg", "mpg"],
    MediaType.Audio: ["aac", "mp3", "flac", "ogg", "m4a", "wav", "wma"],
    MediaType.Image: ["jpg", "jpeg", "png", "gif"]
}
FFMPEG_SUPPORTED_EXTENSIONS = sum(FFMPEG_SUPPORTED_EXTENSIONS_BY_TYPE.values(), [])
FFMPEG_SUPPORTED_EXTENSIONS_REGEX = {k: compile_extension_regex(*v) for k, v in FFMPEG_SUPPORTED_EXTENSIONS_BY_TYPE.items()} 

def ffmpeg_supports(filename):
    for type in FFMPEG_SUPPORTED_EXTENSIONS_BY_TYPE.keys():
        if ffmpeg_supports_type(type, filename):
            return True
    return False

def ffmpeg_supports_types(types, filename):
    for type in types:
        if ffmpeg_supports_type(type, filename):
            return True
    return False

def ffmpeg_supports_type(type, filename):
    return FFMPEG_SUPPORTED_EXTENSIONS_REGEX[type].match(filename.suffix)
