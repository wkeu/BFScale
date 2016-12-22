import numpy as np
from scipy.spatial import distance as dist
import cv2
import imutils
from Measurement_class import Measurement

#Global Definitions
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
PINK = (255, 0, 255)
WHITE = (255, 255, 255)
CYAN = (255,255,0)
Contour_threshold_Area = 400 #TODO:Make this a value of related to the resolution of the image

class Image:

  #Class Varibles
  ref_width = 0.9 #Size of a coin
  ref_object_index = 0 #Hardcoded Value
  measure_object_index =0
  #TODO: Image is a class varible 

  #Class Constructor
  def __init__(self,fname_image,fpath):
      self.fname_image=fname_image
      self.fpath=fpath
  #
  # Class Methods
  #
  #TODO:Not clear the difference between x_cord and x_cordinate
  def midpoint(self,x_cord, y_cord):
        x_cordinate = (x_cord[0] + y_cord[0]) * 0.5
        y_cordinate = (x_cord[1] + y_cord[1]) * 0.5
        return (x_cordinate, y_cordinate)

  def update_measure_object_index(self,measure_object_index):
      self.measure_object_index=measure_object_index-1 #Offset due to indexing of arrays

  def update_ref_object_index(self,ref_object_index):
      self.ref_object_index=ref_object_index-1 #Offset due to indexing of arrays
      

  #TODO:Comment on how it works
  def get_pixel_per_unit(self,ref_object, ref_width):
        box = self.get_bounding_box(ref_object)
        points = self.get_distance_cordinate_points(box)
        distX, distY = points[0][0], points[0][1] #TODO: Bad Smell distX never used
        pixelsPerUnit = distY / ref_width
        dimensionY = distY / pixelsPerUnit
       # print("sucessful excution of get_pixel_per_unit")
       # print("ref object is :" + str(ref_object))
        if dimensionY == ref_width:
          print("dimensionY == ref_width")
        return pixelsPerUnit


  def get_bounding_box(self, c):
    box = cv2.minAreaRect(c)
    print("box calling ", box)
   # print("c is :" + str(c)) ATM contors array being passed in here 
    #TODO:Is this nessary
    if imutils.is_cv2():
        box = cv2.cv.BoxPoints(box)
    else:
        box = cv2.boxPoints(box)

    box = np.array(box, dtype="int")
    #box = imutils.perspective.order_points(box) Function no longer callable
    print("sucessful excution of get_bounding_box")
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
    print("sucessful excution of get_distance_cordinate_points")
    distX = dist.euclidean((X_top_left_top_right, Y_top_left_top_right),
                           (X_bottom_left_bottom_right, Y_bottom_left_bottom_right))
    distY = dist.euclidean((X_top_left_bottom_left, Y_top_left_bottom_left),
                           (X_top_right_bottom_right, Y_top_right_bottom_right))

    return ((distX, distY), (
    (X_top_left_top_right, Y_top_left_top_right), (X_bottom_left_bottom_right, Y_bottom_left_bottom_right),
    (X_top_left_bottom_left, Y_top_left_bottom_left), (X_top_right_bottom_right, Y_top_right_bottom_right)))

  def extract_contors_and_import_image(self):
      # read the image
      # image = cv2.imread(args["image"])
      image = cv2.imread(self.fname_image)
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
      print("sucessful excution of extract_contors_and_import_image")
      return cntores, image

  #TODO: Xtop_left... can be extracted so that we are only inserting (shape,orig,ppu)
  #TODO: Add colour as an input parameter
  #TODO:
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

  def draw_points_on_corners(self, X_bottom_left_bottom_right, X_top_left_bottom_left, X_top_left_top_right,
                             X_top_right_bottom_right, Y_bottom_left_bottom_right, Y_top_left_bottom_left,
                             Y_top_left_top_right, Y_top_right_bottom_right, orig):
      # draw the midpoints on the image
      # TODO: Bad Smell, repeditive code, Should be created into its own object
      # TODO: Replace numbers 5 and -1 with something more meaningfull
      cv2.circle(orig, (int(X_top_left_top_right), int(Y_top_left_top_right)), 5, RED, -1)
      cv2.circle(orig, (int(X_bottom_left_bottom_right), int(Y_bottom_left_bottom_right)), 5, RED, -1)
      cv2.circle(orig, (int(X_top_left_bottom_left), int(Y_top_left_bottom_left)), 5, RED, -1)
      cv2.circle(orig, (int(X_top_right_bottom_right), int(Y_top_right_bottom_right)), 5, RED, -1)
  
  def generate_index_image(self):
    #TODO:Bad smell no need to pass self.fname_image
    #Import image and extract contors
    #TODO:Cntores should be a class varible as should image
    cntores, image = self.extract_contors_and_import_image()
    
    # TODO: comment on whats happening here, the if statment is never used
    # TODO:
    #Wil not work without this line, dont know why
    cnt = cntores[1] #Extract Each object
    ref_object=cnt[self.ref_object_index] #Extract this magic number so it is ref_object index
    
    #TODO:Bad smell no need to pass self.ref_width
    pixelsPerUnit = self.get_pixel_per_unit(ref_object, self.ref_width)
    print("calculated unit pixels ", pixelsPerUnit)

    x=0
    orig = image.copy()
    for c in cnt:
        # if the contour is not sufficiently large, ignore it
        print(str(x))        
        x+=1
        if cv2.contourArea(c) < Contour_threshold_Area: #TODO:Function to dicard small measurments
            continue

        #TODO:Why is this line needed
        box = self.get_bounding_box(c)
        
        cv2.drawContours(orig, [box.astype("int")], -1, GREEN, 2) #Draw green box around Object


        points = self.get_distance_cordinate_points(box)
        # TODO: Bad Smell Code is repiitive and unreeadible
        distX, distY = points[0][0], points[0][1]
        (X_top_left_top_right, Y_top_left_top_right) = points[1][0]
        (X_bottom_left_bottom_right, Y_bottom_left_bottom_right) = points[1][1]
        (X_top_left_bottom_left, Y_top_left_bottom_left) = points[1][2]
        (X_top_right_bottom_right, Y_top_right_bottom_right) = points[1][3]
        
        self.print_number_on_object(X_top_left_top_right, X_top_right_bottom_right, Y_top_left_top_right,
                                 Y_top_right_bottom_right, x, orig)
       
    #Save Generated Image    
    cv2.imwrite("index_image_"+self.fname_image,orig)
    return("index_image_"+self.fname_image,self.fpath)
    
  def generate_measured_image(self):
    #TODO:Bad smell no need to pass self.fname_image
    #Import image and extract contors
    #TODO:Cntores should be a class varible as should image
    cntores, image = self.extract_contors_and_import_image()
    
    # TODO: comment on whats happening here, the if statment is never used
    # TODO:
    #Wil not work without this line, dont know why
    cnt = cntores[1] #Extract Each object
    ref_object=cnt[self.ref_object_index] #Extract this magic number so it is ref_object index
    
    #TODO:Bad smell no need to pass self.ref_width
    pixelsPerUnit = self.get_pixel_per_unit(ref_object, self.ref_width)
    print("calculated unit pixels ", pixelsPerUnit)

    orig = image.copy()
    
    box = self.get_bounding_box(cnt[self.measure_object_index])

    cv2.drawContours(orig, [box.astype("int")], -1, GREEN, 2) #Draw green box

    points = self.get_distance_cordinate_points(box)
    # TODO: Bad Smell Code is repiitive and unreeadible
    distX, distY = points[0][0], points[0][1]
    (X_top_left_top_right, Y_top_left_top_right) = points[1][0]
    (X_bottom_left_bottom_right, Y_bottom_left_bottom_right) = points[1][1]
    (X_top_left_bottom_left, Y_top_left_bottom_left) = points[1][2]
    (X_top_right_bottom_right, Y_top_right_bottom_right) = points[1][3]
        
        
    # draw lines between the midpoints
    
    self.draw_centre_line(X_bottom_left_bottom_right, X_top_left_bottom_left, X_top_left_top_right,
                              X_top_right_bottom_right, Y_bottom_left_bottom_right, Y_top_left_bottom_left,
                              Y_top_left_top_right, Y_top_right_bottom_right, orig)

    self.print_dimensions_on_object(X_top_left_top_right, X_top_right_bottom_right, Y_top_left_top_right,
                                        Y_top_right_bottom_right, distX, distY, orig, pixelsPerUnit)
    
    cv2.imwrite("measured_image_"+self.fname_image,orig)
    return("measured_image_"+self.fname_image,self.fpath)
      
  def main(self):

    #TODO:Bad smell no need to pass self.fname_image
    #Import image and extract contors
    #TODO:Cntores should be a class varible as should image
    cntores, image = self.extract_contors_and_import_image()
    
    # TODO: comment on whats happening here, the if statment is never used
    # TODO:
    #Wil not work without this line, dont know why
    cnt = cntores[1] #Extract Each object
    ref_object=cnt[self.ref_object_index] #Extract this magic number so it is ref_object index
    
    #TODO:Bad smell no need to pass self.ref_width
    pixelsPerUnit = self.get_pixel_per_unit(ref_object, self.ref_width)
    print("calculated unit pixels ", pixelsPerUnit)

    x=0
    orig = image.copy()
    for c in cnt:
        # if the contour is not sufficiently large, ignore it
        print(str(x))        
        x+=1
        if cv2.contourArea(c) < Contour_threshold_Area:
            continue

        box = self.get_bounding_box(c)
        print("box in main ", box)
       #0 orig = image.copy()  #Copy the image so that we keep the orginal image intact
        cv2.drawContours(orig, [box.astype("int")], -1, GREEN, 2) #Draw green box

        """
        # iterate over the original points to draw circles
        for (x_points, y_points) in box:
            cv2.circle(orig, (int(x_points), int(y_points)), 5, BLUE, -1)
        """

        points = self.get_distance_cordinate_points(box)
        # TODO: Bad Smell Code is repiitive and unreeadible
        distX, distY = points[0][0], points[0][1]
        (X_top_left_top_right, Y_top_left_top_right) = points[1][0]
        (X_bottom_left_bottom_right, Y_bottom_left_bottom_right) = points[1][1]
        (X_top_left_bottom_left, Y_top_left_bottom_left) = points[1][2]
        (X_top_right_bottom_right, Y_top_right_bottom_right) = points[1][3]
        
        
        self.print_number_on_object(X_top_left_top_right, X_top_right_bottom_right, Y_top_left_top_right,
                                 Y_top_right_bottom_right, x, orig)
        # draw lines between the midpoints
        """ 
        self.draw_centre_line(X_bottom_left_bottom_right, X_top_left_bottom_left, X_top_left_top_right,
                              X_top_right_bottom_right, Y_bottom_left_bottom_right, Y_top_left_bottom_left,
                              Y_top_left_top_right, Y_top_right_bottom_right, orig)

        self.print_dimensions_on_object(X_top_left_top_right, X_top_right_bottom_right, Y_top_left_top_right,
                                        Y_top_right_bottom_right, distX, distY, orig, pixelsPerUnit)
        """
        # show the generated image
    cv2.imshow("Image", orig)            
        

"""
Test1
"""
    
"""
#Test of Typical Usecase

fname_raw_image="Image_refrence.jpg"
file_path=""

working_image = Image(fname_raw_image,file_path)
working_image.main()

#Generate Image with numbered objects
fname_index_image,path = working_image.generate_index_image()

#Display this image to user, prenesent with screen to choose ref object number and object to measure number 
#User inputs these numbers, Clicks Okay
measure_object_index=4
ref_object_index=3
#Update Fields in Class
working_image.update_ref_object_index(ref_object_index)
working_image.update_measure_object_index(measure_object_index)


#Generate Image with measurement
fname_measured_image,path = working_image.generate_measured_image()

#Display this measured image to user

"""