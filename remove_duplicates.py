import numpy as np
import cv2
import os
import glob

files = glob.glob("*.txt")
files.sort(key=os.path.getmtime)

# Function that searches the folder for image files, converts them to a tensor
def create_imgs_matrix(directory, px_size=1000):
    global image_files   
    image_files = []
    # create list of all files in directory     
    folder_files = [i for i in os.listdir(directory) if i != '.DS_Store']
    folder_files = [i for i in sorted(folder_files, key=lambda x: int(os.path.splitext(x)[0]))]  
    
    # create images matrix
    imgs_list = []
    for filename in folder_files:
        # decode the image and create the matrix
        img = cv2.imdecode(np.fromfile(directory + filename, dtype=np.uint8), 0)
        if type(img) == np.ndarray:
            # resize the image based on the given compression value
            # img = cv2.resize(img, dsize=(px_size, px_size), interpolation=cv2.INTER_CUBIC)
            imgs_list.append(img)
    imgs_matrix = np.stack(imgs_list)
    return imgs_matrix

def mse(imageA, imageB):
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
    return err