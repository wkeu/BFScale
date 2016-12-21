import numpy as np
from scipy.spatial import distance as dist
import cv2
import imutils

#Global Definitions
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
PINK = (255, 0, 255)
WHITE = (255, 255, 255)
Contour_threshold_Area = 200


class Image:

  #Class Varibles
  ref_width = 2.9

  #Class Constructor
  def __init__(self,fname_image):
      self.fname_image=fname_image
  #
  # Class Methods
  #
  #TODO:Not clear the difference between x_cord and x_cordinate
  def midpoint(self,x_cord, y_cord):
        x_cordinate = (x_cord[0] + y_cord[0]) * 0.5
        y_cordinate = (x_cord[1] + y_cord[1]) * 0.5
        return (x_cordinate, y_cordinate)

  #TODO:Comment on how it works
  def get_pixel_per_unit(self,ref_object, ref_width):
        box = self.get_bounding_box(ref_object)
        points = self.get_distance_cordinate_points(box)
        distX, distY = points[0][0], points[0][1] #TODO: Bad Smell distX never used
        pixelsPerUnit = distY / ref_width
        dimensionY = distY / pixelsPerUnit
        if dimensionY == ref_width:
          print("dimensionY == ref_width")
        return pixelsPerUnit


  def get_bounding_box(self, c):
    box = cv2.minAreaRect(c)
    print("box calling ", box)

    #TODO:Is this nessary
    if imutils.is_cv2():
        box = cv2.cv.BoxPoints(box)
    else:
        box = cv2.boxPoints(box)

    box = np.array(box, dtype="int")
    box = imutils.perspective.order_points(box)
    return box


  def get_distance_cordinate_points(self,box):
    (top_left_point, top_right_point, bottom_right_point, bottom_left_point) = box
    (X_top_left_top_right, Y_top_left_top_right) = self.midpoint(top_left_point, top_right_point)
    (X_bottom_left_bottom_right, Y_bottom_left_bottom_right) = self.midpoint(bottom_left_point, bottom_right_point)

    # calculating midpoints between top-left and top-right points
    (X_top_left_bottom_left, Y_top_left_bottom_left) = self.midpoint(top_left_point, bottom_left_point)
    (X_top_right_bottom_right, Y_top_right_bottom_right) = self.midpoint(top_right_point, bottom_right_point)

    # Computing midpoint between the top-right and bottom-right
    #TODO:Repditive code
    distX = dist.euclidean((X_top_left_top_right, Y_top_left_top_right),
                           (X_bottom_left_bottom_right, Y_bottom_left_bottom_right))
    distY = dist.euclidean((X_top_left_bottom_left, Y_top_left_bottom_left),
                           (X_top_right_bottom_right, Y_top_right_bottom_right))

    return ((distX, distY), (
    (X_top_left_top_right, Y_top_left_top_right), (X_bottom_left_bottom_right, Y_bottom_left_bottom_right),
    (X_top_left_bottom_left, Y_top_left_bottom_left), (X_top_right_bottom_right, Y_top_right_bottom_right)))

  def extract_contors_and_import_image(self, fname_image):
      # read the image
      # image = cv2.imread(args["image"])
      image = cv2.imread(fname_image)
      # convert the image to gray scale, and blur it using GaussianBlur
      gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
      gray = cv2.GaussianBlur(gray, (7, 7), 0)
      # perform edge detection,
      detected_edges = cv2.Canny(gray, 50, 100)
      # perform a dilation
      detected_edges = cv2.dilate(detected_edges, None, iterations=1)
      # perform erosion to close gaps in between object edges
      detected_edges = cv2.erode(detected_edges, None, iterations=1)
      # find contours in the edge map
      cntores = cv2.findContours(detected_edges.copy(), cv2.RETR_EXTERNAL,
                                 cv2.CHAIN_APPROX_SIMPLE)
      return cntores, image

  def main(self):

    # For testing image is in directory
    fname_image = "Image_refrence_4.jpg"
    ref_width = 2.9

    cntores, image = self.extract_contors_and_import_image(fname_image)
    
    # TODO: comment on whats happening here, the if statment is never used
    #Wil not work without this line
    cntores = cntores[0] if imutils.is_cv2() else cntores[1]
    ref_object=cntores[0]
    
    #TODO:
    pixelsPerUnit = self.get_pixel_per_unit(ref_object, ref_width)
    print("calculated unit pixels ", pixelsPerUnit)

    for c in cntores:
        # if the contour is not sufficiently large, ignore it
        if cv2.contourArea(c) < Contour_threshold_Area:
            continue

        box = self.get_bounding_box(c)
        print("box in main ", box)
        orig = image.copy()
        cv2.drawContours(orig, [box.astype("int")], -1, GREEN, 2)

        # iterate over the original points to draw circles
        for (x_points, y_points) in box:
            cv2.circle(orig, (int(x_points), int(y_points)), 5, BLUE, -1)


        points = self.get_distance_cordinate_points(box)
        # TODO: Bad Smell Code is repiitive and unreeadible
        distX, distY = points[0][0], points[0][1]
        (X_top_left_top_right, Y_top_left_top_right) = points[1][0]
        (X_bottom_left_bottom_right, Y_bottom_left_bottom_right) = points[1][1]
        (X_top_left_bottom_left, Y_top_left_bottom_left) = points[1][2]
        (X_top_right_bottom_right, Y_top_right_bottom_right) = points[1][3]

        # draw the midpoints on the image
        #TODO: Bad Smell, repeditive code, Should be created into its own object
        #TODO: Replace numbers 5 and -1 with something more meaningfull
        cv2.circle(orig, (int(X_top_left_top_right), int(Y_top_left_top_right)), 5, RED, -1)
        cv2.circle(orig, (int(X_bottom_left_bottom_right), int(Y_bottom_left_bottom_right)), 5, RED, -1)
        cv2.circle(orig, (int(X_top_left_bottom_left), int(Y_top_left_bottom_left)), 5, RED, -1)
        cv2.circle(orig, (int(X_top_right_bottom_right), int(Y_top_right_bottom_right)), 5, RED, -1)

        # draw lines between the midpoints
        cv2.line(orig, (int(X_top_left_top_right), int(Y_top_left_top_right)),
                 (int(X_bottom_left_bottom_right), int(Y_bottom_left_bottom_right)),
                 PINK, 2)
        cv2.line(orig, (int(X_top_left_bottom_left), int(Y_top_left_bottom_left)),
                 (int(X_top_right_bottom_right), int(Y_top_right_bottom_right)),
                 PINK, 2)

        # Drawing the objects according to their size on the image
        cv2.putText(orig, "{:.1f}in".format(distX / pixelsPerUnit),
                    (int(X_top_left_top_right - 15), int(Y_top_left_top_right - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                    WHITE, 2)
        cv2.putText(orig, "{:.1f}in".format(distY / pixelsPerUnit),
                    (int(X_top_right_bottom_right + 10), int(Y_top_right_bottom_right)), cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                    WHITE, 2)

        # show the generated image
        cv2.imshow("Image", orig)
        cv2.waitKey(0)

#Test of the code
test_image=Image("Image_refrence_4.jpg")
test_image.main()

