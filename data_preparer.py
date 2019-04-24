import numpy as np
import pickle
import cv2
import matplotlib.pyplot as plt
import os
import pandas as pd

class DataPreparer():
    def __init__(self, saa_image_name):
        self.saa_image_name = saa_image_name
        self.saa_image = cv2.imread('SAA_images/{}'.format(saa_image_name))
        # coordinates for start of smaller image
        self.start_x = 0
        self.start_y = 0
        
    def split_image(self, start_x, start_y, img_size):
        # x and y origin are in top left corner
        # y covers array rows, x covers array columns (counter intuitive)
        row_min = start_y
        row_max = start_y + img_size
        col_min = start_x
        col_max = start_x + img_size
        
        img = self.saa_image[row_min:row_max, col_min:col_max]
        return img

    def get_threshold(self, img):
        # applies light threshold to image
        # takes any pixel value >= 200 and sets it to 255 (white). All else is black
        # returns image as np array (as per usual)

        threshold = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)[1]

        # turn into a gray image to find contours
        thresh_gray = cv2.cvtColor(threshold, cv2.COLOR_BGR2GRAY)

        return thresh_gray

    def get_contours(self, img):
        # returns coordinates of bright spots in image

        contours, hierarchy = cv2.findContours(img, 1, 2)
        return contours

    def resize_image(self, img, size):
        # makes images smaller than desired size larger to fit size

        height, width = img.shape[0], img.shape[1]

        top = size - height # amount added to top of img
        bottom = 0 # add nothing to bottom
        left = size - width # amount added to left of img
        right = 0 # add nothing to right

        BLACK = [0,0,0]
        new_img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value = BLACK)

        return new_img

    def get_bright_spot(self, img, index, size, contours, resize_img = True):
        # takes position of contour in image and returns smaller image containing that contour
        contour = contours[index]
        if len(contour) > 1: 
            # a cheap workaround. Honestly not entirely sure what it is that the "get_contours" function is return above, but this works. For some reason it's sometimes different sizes, and the first item is the one I want
            contour = contour[0]

        # draws the smallest possible bounding rectangle around bright spot (contour) and gives the top left corner of it, with the width and height
        x, y, w, h = cv2.boundingRect(contour)
        # want to take the middle of the bright spot. Remember that the origin of the image is in the top left
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

    def plot_bright_spots(self, data, labels, set_labels=False):
        fig = plt.figure()

        columns = int(np.sqrt(len(data)))
        rows = int(len(data)/columns)+1

        for i in range(0, rows*columns):
            if i < len(data):
                img_new = data[i][0]
                x = data[i][1]
                y = data[i][2]
                if set_labels:
                    label = labels['label'].iloc[i]

            else:
                img_new = np.random.randint(10, size=(1, 1))
                x = 0
                y = 0
                label = 8

            ax = fig.add_subplot(rows, columns,i+1)
            if set_labels:
                ax.set_title("{}: {}".format(i, label))
            else:
                ax.set_title('{}: {},{}'.format(i,x,y))
            
            ax.imshow(img_new)

        plt.show()
        return

    def save_data(self, path, name, data, labels):
        # saves images in a folder and their data in a file
        # data goes: img_num, x, y, label, img_source

        file_name = "{}{}".format(path, name)

        # check if the file exists and act accordingly
        exists = os.path.isfile(file_name)
        if exists:
            # check the number of the last image created, and start adding new ones from there
            file = open(file_name, "r")
            last_line = file.readlines()[-1]
            last_data = last_line.split(",")
            start_num = last_data[0]
            if start_num != "img_num":
                start_num = int(start_num) + 1
            else:
                start_num = 0
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
            label = labels['label'].iloc[i]

            # save image to folder
            cv2.imwrite(os.path.join(path, '{}.png'.format(image_name)), image)
            # write image data to file
            file.write('{},{},{},{},{}\n'.format(image_name,x,y,label, self.saa_image_name))

        file.close()
        
        return

    def run(self, plot_data=False, save_data=False, set_labels=False):
        # SETUP
        batch = 5
        labels_file_name = "processed_images/labels/labels_{}.txt".format(batch)
        labels = pd.read_csv(labels_file_name, delimiter=",", engine='python')

        # get smaller part of saa_image for processing
        img_size = 100
        self.start_x = 0 + img_size*batch
        self.start_y = 0 #+ img_size*batch

        sample_image = self.split_image(start_x = self.start_x, start_y = self.start_y, img_size = img_size)
        # detect bright spots
        threshold_image = self.get_threshold(sample_image)
        # get bright spot locations
        contours = self.get_contours(threshold_image)

        # GENERATE IMAGES
        # each row in data contains bright spot image, x and y coordinates
        data = []
        for i in range(0, len(contours)-1):
            img_small, x, y = self.get_bright_spot(sample_image, i, 6, contours)
            x = x + self.start_x
            y = y + self.start_y
            data.append([img_small, x, y])

        # plot data
        if plot_data:
            self.plot_bright_spots(data, labels, set_labels = set_labels)
            #self.plot_bright_spots(data, labels)

        # save data
        if save_data:
            path = "processed_images/"
            name = "data.txt"
            self.save_data(path,name,data, labels)


if __name__ == '__main__':
    saa_name = 'saa_img1.png'
    data_preparer = DataPreparer(saa_image_name = saa_name)
    data_preparer.run(plot_data = True, set_labels=True)
    #data_preparer.run(plot_data = True, set_labels=False)
    #data_preparer.run(save_data=True)
    #data_preparer.run()
