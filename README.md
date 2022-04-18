# Automedia

Automedia is a tool to manage large media libraries, whether it be audio or video.

The tool currently supports the following operations:

 * Printing/logging to list media files
 * Verification of media correctness via `ffmpeg` (test-decoding of supported files)
 * Transcoding media libraries to other formats via `ffmpeg`
 * PAR2 creation and verification

## Installation

Automedia can be installed via pip, or can be run with all binary dependencies in a Docker container. 

### Via pip

Automedia is available as a `pip` package. You can download it with:

```bash
pip install automedia
automedia --help
```

### Via Docker

If you wish to run Automedia via Docker, a script has been provided that transparently runs Automedia on your machine as
if it were not running within a container (by mounting the entire root of your drive within the container).

This script may be copied to a directory on your local `$PATH` and will automatically invoke the appropriate Docker container.

```bash
cp automedia-docker /usr/local/bin/automedia
automedia --help
```

## Usage

Print a list of media files we find:

`automedia --root /media print`

Verify the media files we find using `ffmpeg`:

`automedia --root /media verify`

Transcode the media files from `/media` to `/mnt/usb_stick` to 64k AAC format:

`automedia --root /media transcode --preset aac-64k --output=/mnt/usb_stick`

Transcode the media files from `/media` to `/mnt/usb_stick` to FLAC format:

`automedia --root /media transcode --preset flac --output=/mnt/usb_stick`

Create PAR2 files for the media files we find:

`automedia --root /media par2-create`

Verify PAR2 files for the media files we find:

`automedia --root /media par2-verify`
