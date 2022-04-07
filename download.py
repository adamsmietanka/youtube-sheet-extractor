import sys
import os
import shutil

from pytube import YouTube
import ffmpeg
import numpy as np
import cv2
from fpdf import FPDF

class Extractor(YouTube):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dir = f'src/{self.title}'
        self.dir_img = f'src/{self.title}/img'
        self.dir_unique = f'src/{self.title}/unique'

    def sorted_files(self, directory):
        folder_files = [i for i in os.listdir(directory) if i.endswith('.jpg')]
        return [i for i in sorted(folder_files, key=lambda x: int(os.path.splitext(x)[0]))]  

    def download_movie(self):
        vid = self.streams.filter(file_extension='mp4').order_by('resolution').desc().first()
        vid.download(output_path=self.dir, filename='video.mp4')

    def read_frames_as_jpeg(self):
        os.makedirs(self.dir_img, exist_ok=True)
        out, _ = (
            ffmpeg
            .input(f'{self.dir}/video.mp4')
            .filter('fps', fps='1/2')
            .output(f'{self.dir_img}/%d.jpg', start_number=0)
            .overwrite_output()
            .run()
        )
        return out

    def create_imgs_matrix(self):
        imgs_list = []
        for filename in self.sorted_files(self.dir_img):
            img = cv2.imdecode(np.fromfile(f'{self.dir_img}/{filename}', dtype=np.uint8), 0)
            imgs_list.append(img)
        imgs_matrix = np.stack(imgs_list)
        return imgs_matrix

    def mse(self, imageA, imageB):
        err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
        err /= float(imageA.shape[0] * imageA.shape[1])
        return err

    def extract_unique_images(self):
        shutil.rmtree(self.dir_unique, ignore_errors=True)
        matrix = self.create_imgs_matrix()
        first_unique_no = 0
        unique_images_filenames = []
        for i in range(len(matrix)):
            mse = self.mse(matrix[first_unique_no], matrix[i])
            if  10000 > mse and mse > 200:
                unique_images_filenames.append(self.sorted_files(self.dir_img)[i])
                first_unique_no = i

        os.makedirs(self.dir_unique, exist_ok=True)

        for file_name in [f'{self.dir_img}/{i}' for i in unique_images_filenames]:
            shutil.copy(file_name, self.dir_unique)

    def split_imgs(self, after_no):
        sorted_files = self.sorted_files(self.dir_unique)
        name_to_number = lambda x: int(os.path.splitext(x)[0])
        files_after_no = [i for i in sorted_files if name_to_number(i) > after_no]
        for i in files_after_no:
            img = cv2.imread(f'{self.dir_unique}/{i}')
            height, width, _ = img.shape

            # Cut the image in half
            height_cutoff = height // 2
            s1 = img[:height_cutoff, :]
            s2 = img[height_cutoff:, :]

            # Save each half
            cv2.imwrite(f"{self.dir_unique}/{name_to_number(i)}.jpg", s1)
            cv2.imwrite(f"{self.dir_unique}/{name_to_number(i) + 1}.jpg", s2) 

    def make_pdf(self):
        pdf = FPDF()
        pdf.set_margin(0)
        pdf.add_page()

        for file_name in self.sorted_files(self.dir_unique):
            pdf.image(f'{self.dir_unique}/{file_name}', w=pdf.epw)

        pdf.output(f'{self.dir}/sheet.pdf')

    
yt = Extractor("https://www.youtube.com/watch?v=UWeSrfE35Wc")

yt.download_movie()
yt.read_frames_as_jpeg()
yt.extract_unique_images()
yt.split_imgs(5)
yt.make_pdf()