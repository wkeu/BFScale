import numpy as np
from scipy.spatial import distance as dist
import cv2
import imutils
from Measurement_class import Measurement

# Global Definitions
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
PINK = (255, 0, 255)
WHITE = (255, 255, 255)
CYAN = (255, 255, 0)
CONTOUR_THRESHOLD_AREA = 400  # TODO:Allow this value to be dynamic based on input image resolution


class Image:
    # Class Varibles
    ref_width = 0.9  # Size of a coin
    ref_object_index = 0  # Initialisation of Parameters
    measure_object_index = 0

    # TODO: Contors a list of class varible, insert into constructor

    # Class Constructor
    def __init__(self, fname_image, fpath):
        self.fname_image = fname_image  # Unprocessed Image
        self.fpath = fpath  # Path to file

    # Class Methods
    def midpoint(self, x_cord, y_cord):
        x_midpoint = (x_cord[0] + y_cord[0]) * 0.5
        y_midpoint = (x_cord[1] + y_cord[1]) * 0.5
        return x_midpoint, y_midpoint

    def update_measure_object_index(self, measure_object_index):
        self.measure_object_index = measure_object_index - 1  # Offset due to indexing of arrays

    def update_ref_object_index(self, ref_object_index):
        self.ref_object_index = ref_object_index - 1  # Offset due to indexing of arrays

    # TODO:Comment on how it works
    def get_pixel_per_unit(self, ref_object):
        box = self.get_bounding_box(ref_object)
        points = self.get_distance_cordinate_points(box)
        print("points are:"+str(points))
        distX, distY = points[0][0], points[0][1]  # TODO: Bad Smell distX never used
        pixelsPerUnit = distY / self.ref_width
        return pixelsPerUnit

    def get_bounding_box(self, c):
        box = cv2.minAreaRect(c)
        print("box calling ", box)
        # print("c is :" + str(c)) ATM contors array being passed in here
        # TODO:Is this nessary
        if imutils.is_cv2():
            box = cv2.cv.BoxPoints(box)
        else:
            box = cv2.boxPoints(box)

        box = np.array(box, dtype="int")
        # box = imutils.perspective.order_points(box) Function no longer callable
        print("sucessful excution of get_bounding_box")
        return box

    def get_distance_cordinate_points(self, box):
        (top_left_point, top_right_point, bottom_right_point, bottom_left_point) = box
        (X_top_left_top_right, Y_top_left_top_right) = self.midpoint(top_left_point, top_right_point)
        (X_bottom_left_bottom_right, Y_bottom_left_bottom_right) = self.midpoint(bottom_left_point, bottom_right_point)

        # calculating midpoints between top-left and top-right points
        (X_top_left_bottom_left, Y_top_left_bottom_left) = self.midpoint(top_left_point, bottom_left_point)
        (X_top_right_bottom_right, Y_top_right_bottom_right) = self.midpoint(top_right_point, bottom_right_point)

        # Computing midpoint between the top-right and bottom-right
        # TODO:Repditive code
        print("sucessful excution of get_distance_cordinate_points")
        distX = dist.euclidean((X_top_left_top_right, Y_top_left_top_right),
                               (X_bottom_left_bottom_right, Y_bottom_left_bottom_right))
        distY = dist.euclidean((X_top_left_bottom_left, Y_top_left_bottom_left),
                               (X_top_right_bottom_right, Y_top_right_bottom_right))

        return ((distX, distY), (
            (X_top_left_top_right, Y_top_left_top_right), (X_bottom_left_bottom_right, Y_bottom_left_bottom_right),
            (X_top_left_bottom_left, Y_top_left_bottom_left), (X_top_right_bottom_right, Y_top_right_bottom_right)))


    def import_image_and_extract_contors(self):
        image = cv2.imread(self.fpath + self.fname_image)                #Read In Image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)                  #Convert to GreyScale
        gray = cv2.GaussianBlur(gray, (7, 7), 0)                        #blur using GaussianBlur
        detected_edges = cv2.Canny(gray, 50, 100)                       #Edge Detection
        detected_edges = cv2.dilate(detected_edges, None, iterations=1) #Dilation
        detected_edges = cv2.erode(detected_edges, None, iterations=1)  #close gaps in between object edges
        cntores = cv2.findContours(detected_edges.copy(),               #contours in the edge map
                                   cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)

        return cntores, image

    # TODO: Xtop_left... can be extracted so that we are only inserting (shape,orig,ppu)
    # TODO: Bad Smell Code is repiitive and unreeadible
    # TODO: Add colour as an input parameter
    def print_dimensions_on_object(self, X_top_left_top_right, X_top_right_bottom_right, Y_top_left_top_right,
                                   Y_top_right_bottom_right, distX, distY, orig, pixelsPerUnit):

        # Drawing the objects according to their size on the image
        cv2.putText(orig, "{:.1f}in".format(distX / pixelsPerUnit),
                    (int(X_top_left_top_right - 15), int(Y_top_left_top_right - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                    WHITE, 2)
        cv2.putText(orig, "{:.1f}in".format(distY / pixelsPerUnit),
                    (int(X_top_right_bottom_right + 10), int(Y_top_right_bottom_right)), cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                    WHITE, 2)

    def print_number_on_object(self, X_top_left_top_right, X_top_right_bottom_right, Y_top_left_top_right,
                               Y_top_right_bottom_right, index, orig):

        # Drawing the objects according to their size on the image
        cv2.putText(orig, format(index),
                    (int(X_top_left_top_right - 15), int(Y_top_left_top_right - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                    CYAN, 2)

    def draw_centre_line(self, X_bottom_left_bottom_right, X_top_left_bottom_left, X_top_left_top_right,
                         X_top_right_bottom_right, Y_bottom_left_bottom_right, Y_top_left_bottom_left,
                         Y_top_left_top_right, Y_top_right_bottom_right, orig):

        cv2.line(orig, (int(X_top_left_top_right), int(Y_top_left_top_right)),
                 (int(X_bottom_left_bottom_right), int(Y_bottom_left_bottom_right)),
                 PINK, 2)
        cv2.line(orig, (int(X_top_left_bottom_left), int(Y_top_left_bottom_left)),
                 (int(X_top_right_bottom_right), int(Y_top_right_bottom_right)),
                 PINK, 2)

    def generate_index_image(self):
        # Import image and extract contors
        # TODO:Cntores should be a class varible as should image
        # TODO:First 3 Lines can be extracted to constructor
        cntores, image = self.import_image_and_extract_contors()
        cnt = cntores[1]  # TODO:Move to import_image_and_extract_contors

        orig = image.copy()
        for index, c in enumerate(cnt):
            #if the contour is below treshold, ignore it
            if cv2.contourArea(c) < CONTOUR_THRESHOLD_AREA:  # TODO:Function to dicard small measurments
                continue

            box = self.get_bounding_box(c)
            cv2.drawContours(orig, [box.astype("int")], -1, GREEN, 2)  # Draw green box around Object

            #Print number on object
            points = self.get_distance_cordinate_points(box)
            distX, distY = points[0][0], points[0][1]
            (X_top_left_top_right, Y_top_left_top_right) = points[1][0]
            (X_bottom_left_bottom_right, Y_bottom_left_bottom_right) = points[1][1]
            (X_top_left_bottom_left, Y_top_left_bottom_left) = points[1][2]
            (X_top_right_bottom_right, Y_top_right_bottom_right) = points[1][3]

            self.print_number_on_object(X_top_left_top_right, X_top_right_bottom_right, Y_top_left_top_right,
                                        Y_top_right_bottom_right, index, orig)

        # Save Generated Image and Return
        cv2.imwrite(self.fpath + "index_image_" + self.fname_image, orig)
        return ("index_image_" + self.fname_image, self.fpath)

    def generate_measured_image(self):
        cntores, image = self.import_image_and_extract_contors()

        cnt = cntores[1]                                    # Extract Each object
        ref_object = cnt[self.ref_object_index]             # Selecting Ref Object

        pixelsPerUnit = self.get_pixel_per_unit(ref_object) # Calculate Pixel Per Unit

        orig = image.copy()

        box = self.get_bounding_box(cnt[self.measure_object_index])  # Generate box for object wished to be measured

        cv2.drawContours(orig, [box.astype("int")], -1, GREEN, 2)    # Draw green box around object of concern


        points = self.get_distance_cordinate_points(box)
        # TODO: Bad Smell Code is repiitive and unreeadible
        distX, distY = points[0][0], points[0][1]
        (X_top_left_top_right, Y_top_left_top_right) = points[1][0]
        (X_bottom_left_bottom_right, Y_bottom_left_bottom_right) = points[1][1]
        (X_top_left_bottom_left, Y_top_left_bottom_left) = points[1][2]
        (X_top_right_bottom_right, Y_top_right_bottom_right) = points[1][3]

        # draw centre line on object
        self.draw_centre_line(X_bottom_left_bottom_right, X_top_left_bottom_left, X_top_left_top_right,
                              X_top_right_bottom_right, Y_bottom_left_bottom_right, Y_top_left_bottom_left,
                              Y_top_left_top_right, Y_top_right_bottom_right, orig)

        self.print_dimensions_on_object(X_top_left_top_right, X_top_right_bottom_right, Y_top_left_top_right,
                                        Y_top_right_bottom_right, distX, distY, orig, pixelsPerUnit)

        cv2.imwrite(self.fpath + "measured_image_" + self.fname_image, orig)
        return ("measured_image_" + self.fname_image, self.fpath)

"""
Class testcase
"""

"""
# Test of Typical Usecase

fname_raw_image = "Image_refrence.jpg"
file_path = "images/"

working_image = Image(fname_raw_image, file_path)

# Generate Image with numbered objects
fname_index_image, path = working_image.generate_index_image()

# Display this image to user, prenesent with screen to choose ref object number and object to measure number
# User inputs these numbers, Clicks Okay
measure_object_index = 4
ref_object_index = 3
# Update Fields in Class
working_image.update_ref_object_index(ref_object_index)
working_image.update_measure_object_index(measure_object_index)

# Generate Image with measurement
fname_measured_image, path = working_image.generate_measured_image()

# Display this measured image to user
"""