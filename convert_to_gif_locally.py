#!/bin/env python

# requires existing clips/ and gifs/ directories
import subprocess
import os
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip


def get_length(filename):
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            filename,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    print(result.stdout)
    return float(result.stdout)


def write_times(video_length, clip_duration):
    with open("times.txt", "w") as f:
        for i in range(0, video_length - 1):
            f.write(str(i) + "-" + str(i + (clip_duration)))
            f.write("\n")


def split_mp4(filename):
    directory_name = filename.removesuffix(".mp4")
    os.mkdir(f"clips/{directory_name}")
    required_video_file = filename
    with open("times.txt") as f:
        times = f.readlines()
    times = [x.strip() for x in times]
    for time in times:
        starttime = int(time.split("-")[0])
        endtime = int(time.split("-")[1])
        target_name = f"clips/{directory_name}/{directory_name}_{str(times.index(time)+1)}.mp4"
        ffmpeg_extract_subclip(required_video_file, starttime, endtime, targetname=target_name)


# Convert clips to gifs
def make_gifs(filename):
    directory_name = filename.removesuffix(".mp4")
    os.mkdir(f"gifs/{directory_name}")
    for file in os.listdir(f"clips/{directory_name}"):
        videoClip = VideoFileClip(f"clips/{directory_name}/{file}")
        videoClip.write_gif(f"gifs/{directory_name}/{file}.gif")
    return


# video_file is the filename of the mp4 you wish to convert to gifs
video_file = input("Input name of MP4 file: ")
video_duration = get_length(video_file)
clip_duration = input("Input desired gif duration in seconds: ")
write_times(int(video_duration), int(clip_duration))
split_mp4(video_file)
make_gifs(video_file.removesuffix(".mp4"))
