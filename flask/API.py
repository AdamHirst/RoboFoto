from flask import Flask, jsonify, request
import base64
from PIL import Image, ImageFilter
import io

app = Flask(__name__)

#The final image transformation
def transformImage(im, category):

	im = im.rotate(45)

	return im


@app.route('/',methods=['POST'])
def getImage():
	#Get image and category from the json request
	currentImage64 = request.json['Image']
	currentCategory = request.json['Category']
	
	#store the image as a bytes not a string
	image_data = currentImage64
	image_data = bytes(image_data, encoding="ascii")

	#Change the bytes to a PIL image
	im = base64.decodebytes(image_data)
	im = Image.open(io.BytesIO(im))

	#Runs the single transform
	im = transformImage(im)

	#Image to bytes file
	in_mem_file = io.BytesIO()
	im.save(in_mem_file, format = "PNG")
	in_mem_file.seek(0)
	img_bytes = in_mem_file.read()

	#Bytes file to string
	base64_encoded_result_bytes = base64.b64encode(img_bytes)
	base64_encoded_result_str = base64_encoded_result_bytes.decode('ascii')

	#Return the final image
	return jsonify({'Image':base64_encoded_result_str})


if (__name__ == 'main'):
	app.run(debug=True, port=8000)