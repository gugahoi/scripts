scripts
=======

Generic Scripts


converter.py
-----------
Recusively finds avi's and mkv's in the directory passed in and converts them to web optimised mp4's with h264/aac codecs at crf 20.
Processes each file one at a time using 2 threads so that pc is still usable (assuming more than 2 threads on CPU). In case the original file is h264, program on remuxes the file to mp4 with the same original codecs

By default does not touch the original file however can be changed so that it deletes it (in code only for now).

Requires: ffmpeg, ffprobe in $PATH and libx264 and aac codecs

> Usage: python /path/to/converter.py /path/to/directory/to/convert


TODO
----
* Allow command line argument for setting no. of threads on runtime
* Allow command line argument to remove original file on runtime
