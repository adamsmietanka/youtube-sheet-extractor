import sys
import os
from pytube import YouTube
import ffmpeg

def read_frames_as_jpeg(title):
    out, _ = (
        ffmpeg
        .input(f'src/{title}/video.mp4')
        .filter('fps', fps='1/10')
        .output(f'src/{title}/img/test-%d.jpg', start_number=0)
        .overwrite_output()
        .run()
    )
    return out

yt = YouTube(str(sys.argv[1]))
yt.streams.filter(file_extension='mp4').order_by('resolution').desc().first().download(output_path='src/'+yt.title, filename='video.mp4')

os.makedirs(f'src/{yt.title}/img/', exist_ok=True)
read_frames_as_jpeg(yt.title)