import sys
import PIL
import numpy
import math
from numpy import clip
from random import random, randint
from PIL import Image, ImageFilter, ImageEnhance, ImageChops
 
 
def score (image):
    #image.save("seen.png")
    image = image.filter(ImageFilter.FIND_EDGES)
    image = image.convert("L")
    image.resize([32,32])
    image = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
    image = image.resize([8,8])
    image_flipped = image.transpose(Image.FLIP_LEFT_RIGHT)
    difference = ImageChops.subtract(image, image_flipped)
    #difference.save("diff.png")
    value = difference.resize([1,1],Image.ANTIALIAS)
    return (1/(value.load()[0,0]+1)) #greater the value the better the image
   
def restrict (val, minval, maxval):
    if val < minval: return minval
    if val > maxval: return maxval
    return val
 
def crop_rotated (angle, image, image_original):
    quadrant = math.floor(angle / (math.pi / 2)) & 3
    if (quadrant & 1) == 0:
        sign_alpha = angle
    else:
        sign_alpha = math.pi - angle
    alpha = (sign_alpha % math.pi + math.pi) % math.pi
 
    bb = [image_original.size[0] * math.cos(alpha) + image_original.size[1] * math.sin(alpha),image_original.size[0] * math.sin(alpha) + image_original.size[1] * math.cos(alpha)]
   
    if image_original.size[0] < image_original.size[1]:
        gamma = math.atan2(bb[0], bb[1])
    else:
        gamma = math.atan2(bb[1], bb[0])
 
    delta = math.pi - alpha - gamma
   
    if image_original.size[0] < image_original.size[1]:
        length = image_original.size[1]
    else:
        length = image_original.size[0]
       
    d = length * math.cos(alpha);
    a = d * math.sin(alpha) / math.sin(delta)
 
    y = a * math.cos(gamma)
    x = y * math.tan(gamma)
 
    return image.crop([x,y,bb[0] - 2 * x,bb[1] - 2 * y])
   
def Magic(im):
    #init
    crop_iterations = 500
    initial_crop_limit = 0.4
    crop_step_size = 0.05
    crop_min_restriction = 0.40
     
    rotation_iterations = 500
    rotation_step_size = 1
     
    #open image
    raw_image = im
     
    #set initial transform variables
    lastscore = 0
    current_score = 0
     
    #find optimal crop
    crop = [random()*initial_crop_limit,random()*initial_crop_limit,random()*initial_crop_limit,random()*initial_crop_limit] #[left,top,right,bottom]
    last_crop = [random()*initial_crop_limit,random()*initial_crop_limit,random()*initial_crop_limit,random()*initial_crop_limit]
    cropdir = [0,0,0,0]
     
     
    image = raw_image.resize([256,256],Image.ANTIALIAS)
     
    for i in range (1,crop_iterations):
        crop = [crop[0]+cropdir[0],crop[1]+cropdir[1],crop[2]+cropdir[2],crop[3]+cropdir[3]]
        transform = image.crop([(crop[0])*256,(crop[1])*256,256-(crop[2])*256,256-(crop[3])*256])
        current_score = score(transform)
       
        if current_score <= lastscore:
            cropdir = [(random()-0.5)*0.05,(random()-0.5)*0.05,(random()-0.5)*0.05,(random()-0.5)*0.05]
            crop = last_crop
           
        crop = [restrict(crop[0],0,crop_min_restriction),restrict(crop[1],0,crop_min_restriction),restrict(crop[2],0,crop_min_restriction),restrict(crop[3],0,crop_min_restriction)]
        lastcrop = crop
        lastscore = current_score
        print("Score:" + str(current_score))
       
    if current_score > lastscore:
            crop = crop
    else:
        crop = last_crop
           
    print("Score:" + str(current_score))
    print("Crop:" + str(crop))
           
    #find optimal rotation
    image = raw_image.crop([(crop[0])*raw_image.size[0],(crop[1])*raw_image.size[1],raw_image.size[0]-(crop[2])*raw_image.size[0],raw_image.size[1]-(crop[3])*raw_image.size[1]])
    image = image.resize([256,256],Image.ANTIALIAS)
     
    rotation = 0
    lastrotation = 0
    rotdir = 1
     
    for i in range (1,rotation_iterations):
        rotation = rotation + rotdir
        transform = image.rotate(rotation, expand=True)
        current_score = score(transform)
       
        if current_score <= lastscore:
            rotdir = (random()-0.5)*rotation_step_size
            rotation = lastrotation
           
        print("Score:" + str(current_score))
        lastscore = current_score
        lastrotation = rotation
       
    if current_score < lastscore:
        rotation = lastrotation
       
           
    #print results
    print("Rotation:" + str(rotation))
    print("Score:" + str(current_score))
    print("Crop:" + str(crop))
     
    #save image
    image = raw_image
    transform = raw_image.crop([(crop[0])*raw_image.size[0],(crop[1])*raw_image.size[1],raw_image.size[0]-(crop[2])*raw_image.size[0],raw_image.size[1]-(crop[3])*raw_image.size[1]])
    transform = transform.rotate(rotation, expand=True)
    #transform = crop_rotated(rotation,transform,raw_image)
     
    # Clean the background noise, if color != white, then set to black.
    return transform