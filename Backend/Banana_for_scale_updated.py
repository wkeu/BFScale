import numpy as np
from scipy.spatial import distance as dist
import argparse
import cv2
import imutils
from imutils import perspective
from imutils import contours

def midpoint(x_cord, y_cord):
	x_cordinate = (x_cord[0]+y_cord[0])*0.5
	y_cordinate = (x_cord[1]+y_cord[1])*0.5
	#return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)
	return (x_cordinate,y_cordinate)

# construct the argument parse and parse the arguments
def parse_arguments():
	parsed_argument = argparse.ArgumentParser()
	parsed_argument.add_argument("-i", "--image", required=True,
	help="path to the input image")
	#ap.add_argument("-w", "--width", type=float, required=True,
	parsed_argument.add_argument("-w", "--reference",  required=True,
	help="Choose reference")
	return vars(parsed_argument.parse_args())

def get_pixel_per_unit(cntores,ref_width):
	pixelsPerunit = 0
	for c in cntores:
		box = get_bounding_box(c)
		points = get_distance_cordinate_points(box)
		distX,distY = points[0][0],points[0][1]
		pixelsPerUnit = distY / ref_width
		dimensionY = distY / pixelsPerUnit
		if dimensionY == ref_width:
			break
	return pixelsPerUnit	
		
def get_bounding_box(c):
	box = cv2.minAreaRect(c)
	print("box calling ",box)
	
	if imutils.is_cv2():
		box = cv2.cv.BoxPoints(box)
	else:
		box = cv2.boxPoints(box)
	
	box = np.array(box, dtype="int")
	box = perspective.order_points(box)
	return box

def get_distance_cordinate_points(box):
	(top_left_point, top_right_point, bottom_right_point, bottom_left_point) = box
	(X_top_left_top_right, Y_top_left_top_right) = midpoint(top_left_point, top_right_point)
	(X_bottom_left_bottom_right, Y_bottom_left_bottom_right) = midpoint(bottom_left_point, bottom_right_point)

	# calculating midpoints between top-left and top-right points
	(X_top_left_bottom_left, Y_top_left_bottom_left) = midpoint(top_left_point, bottom_left_point)
	(X_top_right_bottom_right, Y_top_right_bottom_right) = midpoint(top_right_point, bottom_right_point)
	
	#Computing midpoint between the top-right and bottom-right
	distX = dist.euclidean((X_top_left_top_right, Y_top_left_top_right), (X_bottom_left_bottom_right, Y_bottom_left_bottom_right))
	distY = dist.euclidean((X_top_left_bottom_left, Y_top_left_bottom_left), (X_top_right_bottom_right, Y_top_right_bottom_right))
	
	
	return ((distX,distY),((X_top_left_top_right, Y_top_left_top_right),(X_bottom_left_bottom_right, Y_bottom_left_bottom_right),(X_top_left_bottom_left, Y_top_left_bottom_left),(X_top_right_bottom_right, Y_top_right_bottom_right)))
	
def main():
  #This method will take input arguments and returns it
  #args = parse_arguments() #TODO: Comment is not sufficient, arguments not suffiecient 

  #if args["reference"] =='Coin' or 'coin':
  #ref_width = 2.9  #TODO: No Magic Numbers
	
  #For testing image is in directory
  fname_image="Image_refrence_4.jpg"
  ref_width = 2.9
      
  # read the image
  #image = cv2.imread(args["image"])
  image = cv2.imread(fname_image)
	
  #convert the image to gray scale, and blur it using GaussianBlur
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
  cntores = cntores[0] if imutils.is_cv2() else cntores[1]

  # sort the contours from left-to-right and initialize the
  # 'pixels per metric' calibration variable
  #(cntores, _) = contours.sort_contours(cntores)
		
  pixelsPerUnit = get_pixel_per_unit(cntores,ref_width)
  print("calculated unit pixels ",pixelsPerUnit)
	
  for c in cntores:
		# if the contour is not sufficiently large, ignore it
		if cv2.contourArea(c) < 200:
			continue
		
		box = get_bounding_box(c)
		print("box in main ", box)
		orig = image.copy()
		cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

		# iterate over the original points to draw circles
		for (x_points, y_points) in box:
			cv2.circle(orig, (int(x_points), int(y_points)), 5, (0, 0, 255), -1)
		
		points = get_distance_cordinate_points(box)
		distX,distY = points[0][0],points[0][1]
		(X_top_left_top_right, Y_top_left_top_right) = points[1][0]
		(X_bottom_left_bottom_right, Y_bottom_left_bottom_right) = points[1][1]
		(X_top_left_bottom_left, Y_top_left_bottom_left) = points[1][2]
		(X_top_right_bottom_right, Y_top_right_bottom_right) = points[1][3]
		
		# draw the midpoints on the image
		cv2.circle(orig, (int(X_top_left_top_right), int(Y_top_left_top_right)), 5, (255, 0, 0), -1)
		cv2.circle(orig, (int(X_bottom_left_bottom_right), int(Y_bottom_left_bottom_right)), 5, (255, 0, 0), -1)
		cv2.circle(orig, (int(X_top_left_bottom_left), int(Y_top_left_bottom_left)), 5, (255, 0, 0), -1)
		cv2.circle(orig, (int(X_top_right_bottom_right), int(Y_top_right_bottom_right)), 5, (255, 0, 0), -1)
		
		# draw lines between the midpoints
		cv2.line(orig, (int(X_top_left_top_right), int(Y_top_left_top_right)), (int(X_bottom_left_bottom_right), int(Y_bottom_left_bottom_right)),
		(255, 0, 255), 2)
		cv2.line(orig, (int(X_top_left_bottom_left), int(Y_top_left_bottom_left)), (int(X_top_right_bottom_right), int(Y_top_right_bottom_right)),
		(255, 0, 255), 2)
		
            #TODO: Bad Smell 
		dimensionX = distX / pixelsPerUnit
		dimensionY = distY / pixelsPerUnit
		
		# Drawing the objects according to their size on the image
		cv2.putText(orig, "{:.1f}in".format(distX / pixelsPerUnit),
			(int(X_top_left_top_right - 15), int(Y_top_left_top_right - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
		cv2.putText(orig, "{:.1f}in".format(distY / pixelsPerUnit),
			(int(X_top_right_bottom_right + 10), int(Y_top_right_bottom_right)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

		# show the generated image
		cv2.imshow("Image", orig)
		cv2.waitKey(0)

main()