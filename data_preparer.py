"""
This notebook takes a subsection of an SAA image and identifies
bright spots from it. It turns these bright spots into smaller
images, prompts the user for classification, and saves this data.

It also allows for review of previously made data.
"""

import numpy as np
import pickle
import cv2
import matplotlib.pyplot as plt
import os
import pandas as pd
from tqdm import tqdm

class DataPreparer():
    def __init__(self, saa_image_name, sub_img_size = 100):
        """
        Loads saa image and sets start coords and size for
        new subsection of image
        """
        self.saa_image_name = saa_image_name
        self.saa_image = cv2.imread('SAA_images/{}'.format(saa_image_name))
        # Size of extracted subsection of SAA image
        self.sub_img_size = sub_img_size
        # coordinates for start of smaller image
        self.start_x = 0
        self.start_y = 0
        
    def split_image(self):
        """
        Returns subsection of larger SAA image
        """
        # x and y origin are in top left corner
        # y covers array rows, x covers array columns (counter intuitive)
        row_max = self.start_y + self.sub_img_size
        col_max = self.start_x + self.sub_img_size
        
        img = self.saa_image[self.start_y:row_max, self.start_x:col_max]
        return img

    def get_threshold(self, img):
        """
        Applies light threshold to image by taking any pixel value 
        >= 200 and sets it to 255 (white). All else is black.
        Converts image to gray as well.

        Returns image as np array (as per usual)
        """

        threshold = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)[1]

        # turn into a gray image to find contours
        thresh_gray = cv2.cvtColor(threshold, cv2.COLOR_BGR2GRAY)

        return thresh_gray

    def get_contours(self, img):
        """
        Returns coordinates of bright spots in image
        """

        contours, hierarchy = cv2.findContours(img, 1, 2)
        return contours

    def resize_image(self, img, size):
        """
        Makes bright spot images larger if cut off from edges

        Returns resized image
        """

        height, width = img.shape[0], img.shape[1]

        top = size - height # amount added to top of img
        bottom = 0 # add nothing to bottom
        left = size - width # amount added to left of img
        right = 0 # add nothing to right

        BLACK = [0,0,0]
        new_img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value = BLACK)

        return new_img

    def get_bright_spot(self, img, index, size, contours, resize_img = True):
        """
        takes position of contour in image and returns smaller image 
        containing that contour
        """
        contour = contours[index]
        if len(contour) > 1: 
            # a cheap workaround. Honestly not entirely sure what it is
            # that the "get_contours" function is returning above, but this
            # works. For some reason it's sometimes different sizes, and
            # the first item is the one I want
            contour = contour[0]

        # draws the smallest possible bounding rectangle around bright spot 
        # (contour) and gives the top left corner of it, with the width and height
        x, y, w, h = cv2.boundingRect(contour)
        # want to take the middle of the bright spot. Remember that the 
        # origin of the image is in the top left
        row_mid = y + h/2
        col_mid = x + w/2

        row_min = int(row_mid - (size/2))
        row_max = int(row_mid + (size/2))
        col_min = int(col_mid - (size/2))
        col_max = int(col_mid + (size/2))

        # sometimes the image is on the edge of the frame:
        rows, cols = img.shape[0], img.shape[1]
        if row_min < 0:
            row_min = 0
        if col_min < 0:
            col_min = 0
        if row_max > rows-1:
            row_max = rows-1
        if col_max > cols-1:
            col_max = cols-1

        img_small = img[row_min:row_max, col_min:col_max]

        if resize_img:
            height, width = img_small.shape[0], img_small.shape[1]
            if height != size or width != size:
                img_small = self.resize_image(img_small, size)

        # return image of bright spot and coordinates in original image
        # image, x, y
        return img_small, col_mid, row_mid

    def review_data(self, path, filename, start_img_num, end_img_num, old_naming=False):
        """
        Plots requested images with image number and classifications
        """
        fig = plt.figure()

        full_path = path + '/' + filename
        all_data = pd.read_csv(full_path, delimiter=",",engine="python")
        all_data.set_index('img_num')
        data = all_data.iloc[start_img_num:end_img_num+1]

        columns = int(np.sqrt(len(data)))
        rows = int(len(data)/columns)+1

        for i in tqdm(data.index.tolist()):
            if not old_naming:
                img_name = path+'/{}_{}.png'.format(filename, i)
            else:
                img_name = path+'/{}.png'.format(i)
            img_new = cv2.imread(img_name)
            x = data.iloc[i]['x']
            y = data.iloc[i]['y']
            label = data.iloc[i]['label']

            ax = fig.add_subplot(rows, columns,i+1)
            ax.set_title("{}: {}".format(i, label), color = 'r', fontsize=10)
            
            ax.imshow(img_new)

        fig.tight_layout(pad=1.0)
        plt.show()
        return

    def save_data(self, path, filename, data):
        """
        saves images in a folder and their data in a file
        data goes: img_num, x, y, label, img_source
        """

        file_name = "{}/{}".format(path, filename)
        start_num = 0

        # check if the data file exists and act accordingly
        if os.path.isfile(file_name):
            # check the number of the last image created, and start adding new ones from there
            file = open(file_name, "r")
            last_line = file.readlines()[-1]
            last_data = last_line.split(",")
            start_num = last_data[0]
            if start_num != "img_num":
                start_num = int(start_num) + 1
            file.close()
            file = open(file_name, "a")
        else:
            # create a file with headings
            file = open(file_name, "a+")
            file.write("img_num,x,y,label,img_source\n")
            start_num = 0

        for i in range(0, len(data)):
            image_name = str(i+start_num)
            image = data[i][0]
            x = data[i][1]
            y = data[i][2]
            label = data[i][3]

            # save image to folder
            cv2.imwrite(os.path.join(path, '{}_{}.png'.format(filename, image_name)), image)
            # write image data to file
            file.write('{},{},{},{},{}\n'.format(image_name,x,y,label, self.saa_image_name))

        file.close()
        
        return

    def create_and_classify_images(self, path, filename, row=0, column=0, save_data=True):
        """
        Creates images of bright spots from larger SAA image.
        Displays smaller images and asks for classification.
        Saves image data in array with items [image, x, y, classification]
        """
        ### Get subsection of SAA Image
        self.start_x = self.sub_img_size * column
        self.start_y = self.sub_img_size * row

        # Take subsection of SAA image
        sub_img = self.split_image()
        # Detect bright spots
        threshold_img = self.get_threshold(sub_img)
        # Get bright spot locations
        contours = self.get_contours(threshold_img)

        ## Get bright spots in subsection
        # Each row in data contains bright spot image, xy coords
        imgs_data = []
        for i in range(0, len(contours)-1):
            bright_img, x, y = self.get_bright_spot(sub_img, i, 6, contours)
            # translate coordinates to original SAA image
            x = x + self.start_x
            y = y + self.start_y

            ## GET CLASSIFICATION
            # Display image
            plt.imshow(bright_img)
            plt.show(block=False)
            print("Please enter the classification (1 for cosmic ray, 0 if not):")
            classification = input()
            while not (classification=="0" or classification=="1"):
                print("Please enter a valid classification")
                classification = input()
            plt.close()

            imgs_data.append([bright_img, x, y, classification])

        if save_data:
            self.save_data(path, filename, imgs_data)

        return imgs_data

if __name__ == '__main__':
    saa_name = 'saa_img1.png'
    data_preparer = DataPreparer(saa_image_name = saa_name)

    ## Create new images and classify
    path = "processed_images"
    filename = "data.txt"
    # data_preparer.create_and_classify_images(path, filename, save_data = False)

    ## Load previous images to review
    start_img_num = 0
    end_img_num = 11
    data_preparer.review_data(path, filename, start_img_num, end_img_num, old_naming=True)
