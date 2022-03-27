from dataclasses import dataclass
import sys
import os
import shutil

from pytube import YouTube
import ffmpeg

from remove_duplicates import create_imgs_matrix, mse

def read_frames_as_jpeg(title):
    out, _ = (
        ffmpeg
        .input(f'src/{title}/video.mp4')
        .filter('fps', fps='1/10')
        .output(f'src/{title}/img/%d.jpg', start_number=0)
        .overwrite_output()
        .run()
    )
    return out
    
# yt = YouTube("https://www.youtube.com/watch?v=SEwqRF-_hsk")
# yt.streams.filter(file_extension='mp4').order_by('resolution').desc().first().download(output_path='src/'+yt.title, filename='video.mp4')

@dataclass
class YtMock:
    title: str

yt = YtMock(title='Somewhere Over The Rainbow. Arranged for solo piano, with music sheet.')

directory = f'src/{yt.title}/'

# os.makedirs(directory + 'img/', exist_ok=True)
# read_frames_as_jpeg(yt.title)

matrix = create_imgs_matrix(directory + 'img/')

first_unique_no = 0
unique_images = [0]
for i in range(1, len(matrix)):
    if mse(matrix[first_unique_no], matrix[i]) > 200:
        unique_images.append(i)
        first_unique_no = i

os.makedirs(directory + 'unique', exist_ok=True)

for file_name in [f'{directory}img/{i}.jpg' for i in unique_images]:
    full_file_name = os.path.abspath(file_name)
    shutil.copy(file_name, directory + 'unique')