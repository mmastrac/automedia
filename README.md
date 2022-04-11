# Automedia

Automedia is a tool to manage large media libraries, whether it be audio or video.

The tool currently supports the following operations:

 * Printing/logging to list media files
 * Verification of media correctness via `ffmpeg` (test-decoding of supported files)
 * PAR2 creation and verification

## Installation

Automedia can be installed directly on your system, or can be run - with all dependencies - in a docker container. If
you wish to run Automedia via docker, a script has been provided that transparently runs Automedia on your machine as
if it were not running within a container (by mounting the entire root of your drive within the container).

## Usage

Print a list of media files we find:

`automedia --root /media print`

Verify the media files we find using `ffmpeg`:

`automedia --root /media verify`

Create PAR2 files for the media files we find:

`automedia --root /media par2-create`

Verify PAR2 files for the media files we find:

`automedia --root /media par2-verify`
