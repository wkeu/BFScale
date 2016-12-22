import os
import sys
from flask import Flask, render_template, request, send_from_directory
from Image_class import Image
# from flask_bootstrap import Bootstrap

__author__ = 'ibininja'

app = Flask(__name__)
# Bootstrap(app)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/upload", methods=['GET', 'POST'])
def upload():
	target = os.path.join(APP_ROOT,'images/')
	print(target)

	if not os.path.isdir(target):
		os.mkdir(target)

	for file in request.files.getlist("file"):
		print(file)
		filename = file.filename
		destination = "/".join([target, filename])
		print(destination)
		# print >> sys.stderr, destination
		file.save(destination)
# Pass the place where the image is stored through this render
	return render_template("complete.html")

@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)

@app.route('/gallery')
def get_gallery():
    image_names = os.listdir('./images')
    print(image_names)
    return render_template("gallery.html", image_names=image_names)

@app.route('/upload/user_input', methods=['GET','POST'])
def select():
	target_object = request.values['target_object']
	ref_object = request.values['ref_object']

	return render_template("index.html")


if __name__=="__main__":
	app.run(port=4555, debug=True)

#	
#Code to be put in, Order things will happen in
#

#Upload image, save as destination

#Creat instance of class
working_image = Image(fname_raw_image,path)

#Generate Image with numbered objects
fname_index_image,path = working_image.generate_index_image()

#Display this image to user, prenesent with screen to choose ref object number and object to measure number 
#User inputs these numbers, Clciks Okay

#Update Fields in Class
working_image.update_ref_object_index(ref_object_index)
working_image.update_measure_object_index(measure_object_index)

#Generate Image with measurement
fname_measured_image,path = working_image.generate_measured_image()

#Display this measured image to user