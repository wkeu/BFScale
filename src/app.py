import os
import sys
from flask import Flask, render_template, request, send_from_directory
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

