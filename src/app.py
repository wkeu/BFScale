import os
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
		file.save(destination)

	return render_template("complete.html")

# @app.route('/upload/<filename>')
# def send_image(filename):
#     return send_from_directory("images", filename)

# @app.route('/index/<filename>')
# def send_bootstrap(filename):
# 	print("Check")
# 	print("Filename:", filename)
# 	return send_from_directory("templates/assets/css", filename)

if __name__=="__main__":
	app.run(port=4555, debug=True)