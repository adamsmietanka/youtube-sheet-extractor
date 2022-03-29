import sys
import os
import shutil

from pytube import YouTube
import ffmpeg
from fpdf import FPDF

from remove_duplicates import create_imgs_matrix, mse

def read_frames_as_jpeg(directory):
    os.makedirs(directory + 'img/', exist_ok=True)
    out, _ = (
        ffmpeg
        .input(f'{directory}/video.mp4')
        .filter('fps', fps='1/2')
        .output(f'{directory}/img/%d.jpg', start_number=0)
        .overwrite_output()
        .run()
    )
    return out

def extract_unique_images(matrix):
    first_unique_no = 0
    unique_images = [0]
    for i in range(1, len(matrix)):
        if mse(matrix[first_unique_no], matrix[i]) > 200:
            unique_images.append(i)
            first_unique_no = i

    os.makedirs(directory + 'unique', exist_ok=True)

    for file_name in [f'{directory}img/{i}.jpg' for i in unique_images]:
        shutil.copy(file_name, directory + 'unique')

def make_pdf(directory):
    pdf = FPDF()
    pdf.set_margin(0)
    pdf.add_page()

    for file_name in [i for i in os.listdir(directory + 'unique') if i.endswith('.jpg')]:
        pdf.image(f'{directory}unique/{file_name}', w=pdf.epw)

    pdf.output(directory + 'sheet.pdf')

    
yt = YouTube("https://www.youtube.com/watch?v=QpeLM71Q9D0")
yt.streams.filter(file_extension='mp4').order_by('resolution').desc().first().download(output_path='src/'+yt.title, filename='video.mp4')

directory = f'src/{yt.title}/'

read_frames_as_jpeg(directory)

matrix = create_imgs_matrix(directory + 'img/')
extract_unique_images(matrix)
make_pdf(directory)