#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Gustavo Hoirisch <gugahoi@gmail.com>
import os
import sys
import subprocess
import json
from multiprocessing import Pool, Lock

printlock = Lock()
queuelock = Lock()
rmOriginal = False

def findExtension(dirlist, extension):
    """
    Keyword arguments:
    dirlist -- a list of directories to search in
    extension -- file extension to search for (.avi, .mp4, etc...)
    """
    result = []
    for dirname in dirlist:
        for root, dirs, files in os.walk(dirname):
            for name in files:
                if name.endswith(extension):
                    result.append(os.path.abspath(root + '/' + name))
    return result

def output(txt):
    printlock.acquire()
    print txt
    printlock.release()

def remux(src, dst):
    # "ffmpeg -i $f -codec copy -map 0 -movflags faststart $FULLPATH$filename.tmp.mp4"
    args = ['ffmpeg', '-i', src, '-codec', 'copy', '-map', '0', '-movflags', 'faststart', '-threads', '0', dst]
    bitbucket = open('/dev/null')
    try:
        output("Remuxing {} to {}.".format(src, dst))
        subprocess.check_call(args, stdout=bitbucket, stderr=bitbucket)
        output("Remux of {} completed.".format(src))
        if rmOriginal:
            os.remove(src)
    except:
        output("ERROR: Converting {} failed.".format(src))
    bitbucket.close()

def transcode(src, dst):
    # ffmpeg -i "$f" -codec:v libx264 -crf 20 -threads 4 -codec:a aac -strict -2 -movflags faststart "$FULLPATH/$filename.mp4" </dev/null >/dev/null 2>/var/log/ffmpeg.log &
    args = ['ffmpeg', '-i', src, '-codec:v', 'libx264', '-crf', '20', '-codec:a', 'aac', '-strict', 'experimental', '-movflags', 'faststart', '-threads', '0', dst]
    bitbucket = open('/dev/null')
    try:
        output("Converting {} to {}.".format(src, dst))
        subprocess.check_call(args, stdout=bitbucket, stderr=bitbucket)
        if rmOriginal:
            os.remove(src)
        output("Conversion of {} completed.".format(src))
    except:
        output("ERROR: Converting {} failed.".format(src))
    bitbucket.close()


def process(fname):
    """
    Keyword arguments:
    fname -- name of the file to convert
    """
    mp4 = fname[0:-3]+'mp4'

    if os.path.isfile(mp4):
        output('File exists %s, skipping processing.' % (mp4))
        return

    passthrough = False
    # ffprobe -show_format -show_streams -loglevel quiet -print_format json FILE_NAME
    args = ['ffprobe', '-show_format', '-show_streams', '-loglevel', 'quiet', '-print_format', 'json', fname]
    try:
        output("Probing file {}".format(fname))
        info = json.loads(subprocess.check_output(args))
        output("Probe completed.".format(fname))
    except:
        output('ERROR: ffprobe failed')

    for stream in info['streams']:
        if 'video' in stream['codec_type']:
            if stream['codec_name'] == 'h264':
                passthrough = True

    queuelock.acquire()
    if passthrough:
        remux(fname, mp4)
    else:
        transcode(fname, mp4)
    queuelock.release()

def main(argv):
    """Main program.

    Keyword arguments:
    argv -- command line arguments
    """
    if len(argv) == 1:
        path, binary = os.path.split(argv[0])
        print "Usage: {} [directory ...]".format(binary)
        sys.exit(0)
    videos = []
    videos.extend(findExtension(argv[1:], '.avi'))
    videos.extend(findExtension(argv[1:], '.mkv'))
    output('Found %s videos to process' % (len(videos)))
    p = Pool()
    p.map(process, videos)
    p.close()

if __name__ == '__main__':
    main(sys.argv)
