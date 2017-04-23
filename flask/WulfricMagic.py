import sys
import PIL
import math
from random import random, randint
from PIL import Image, ImageFilter, ImageEnhance, ImageChops

def get_palette (filename):
	color_thief = ColorThief(filename)
	palette = color_thief.get_palette(color_count = 6)
	return palette
	
def create_composition_image (image):
	image_edges = image.filter(ImageFilter.FIND_EDGES)
	image_gray = image_edges.convert("L")
	image_composition = image_gray.resize([64,64],Image.ANTIALIAS)
	return image_composition
	
def score (image):
	image_flipped = image.transpose(Image.FLIP_LEFT_RIGHT)
	difference = ImageChops.subtract(image, image_flipped)
	#difference.save("diff.png")
	value = difference.resize([1,1],Image.ANTIALIAS)
	return (1/(value.load()[0,0]+1)) #greater the value the better the image
	
def restrict (val, minval, maxval):
    if val < minval: return minval
    if val > maxval: return maxval
    return val

def Magic(im):
	#open image
	raw_image = im

	#set initial transform variables
	lastscore = 0
	current_score = 0

	#find optimal crop
	crop = [0,0,0,0] #[left,top,right,bottom]
	last_crop = [0.25,0.25,0.25,0.25]
	cropdir = [0,0,0,0]

	image = create_composition_image(raw_image)	

	for i in range (1,2000):
		crop = [crop[0]+cropdir[0],crop[1]+cropdir[1],crop[2]+cropdir[2],crop[3]+cropdir[3]]
		transform = image.crop([(crop[0])*64,(crop[1])*64,64-(crop[2])*64,64-(crop[3])*64])
		current_score = score(transform)
		
		if current_score <= lastscore:
			cropdir = [(random()-0.5)/20,(random()-0.5)/20,(random()-0.5)/20,(random()-0.5)/20]
			crop = last_crop
			
		crop = [restrict(crop[0],0,0.4),restrict(crop[1],0,0.4),restrict(crop[2],0,0.4),restrict(crop[3],0,0.4)]
		lastcrop = crop
		lastscore = current_score
		print("Score:" + str(current_score))
		
	if current_score > lastscore:
			crop = crop
	else:
		crop = last_crop
			
			
	#find optimal rotation
	image = raw_image.crop([(crop[0])*raw_image.size[0],(crop[1])*raw_image.size[1],raw_image.size[0]-(crop[2])*raw_image.size[0],raw_image.size[1]-(crop[3])*raw_image.size[1]])
	#image.save("crop.png")
	image = create_composition_image(image)	

	rotation = 0
	lastrotation = 0
	rotdir = 1

	for i in range (1,360):
		rotation = rotation + rotdir
		transform = image.rotate(rotation)
		
		width_diff = (image.size[0] - (image.size[0]/2)*math.tan(math.radians(rotation)))/2
		height_diff = (image.size[1] - (image.size[1]/2)*math.tan(math.radians(rotation)))/2
		center_x = image.size[0]/2
		center_y = image.size[1]/2
		
		transform = transform.crop([center_x-width_diff,center_y-height_diff,center_x+width_diff,center_y+height_diff])
		current_score = score(transform)
		
		if current_score < lastscore:
			rotdir = random()-0.5
			rotation = lastrotation
			
		print("Score:" + str(current_score))
		lastscore = current_score
		lastrotation = rotation
		
	if current_score > lastscore:
			rotation = rotation
	else:
		rotation = lastrotation
			
	#print results
	print("Rotation:" + str(rotation))
	print("Score:" + str(current_score))
	print("Crop:" + str(crop))

	#save image
	image = raw_image
	transform = raw_image.crop([(crop[0])*raw_image.size[0],(crop[1])*raw_image.size[1],raw_image.size[0]-(crop[2])*raw_image.size[0],raw_image.size[1]-(crop[3])*raw_image.size[1]])
	transform = transform.rotate(rotation)
	return transform