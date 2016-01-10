#!/usr/bin/python
import sys
import random
from PIL import Image
from glob import glob
from random import random
from random import choice

VERTICAL_SIZE_ORGIN = 675
HORIZONTAL_SIZE_ORGIN = 900

stats_y = []
stats_x = []
diff_y = []
split_x = []
factors_y = []
factors_x = []
images = []
size_out = 880, 25519

def analyse():
  stats = open("stats", "r").read().split()
  is_y = True
  
  for i in stats:
    if (is_y):
      stats_y.append((int)(i))
    else:
      stats_x.append((int)(i))
    is_y = not is_y;
  
  
  diff_y.append(stats_y[0])
  
  for i in range(len(stats_y)):
    split_x.append(stats_x[i])
    factor = (float)(split_x[i]) / HORIZONTAL_SIZE_ORGIN
    factors_x.append(factor)
    if (i + 1 == len(stats_y)):
      break
    previous = stats_y[i]
    current = stats_y[i + 1]
    diff_y.append(current - previous)
    factor = (float)(diff_y[i]) / VERTICAL_SIZE_ORGIN
    factors_y.append(factor)


def load_images():
  for filename in glob("img/*"):
    img = Image.open(filename)
    images.append(img)

def get_region_box(image, drift_x, last_height = 0):
  left = drift_x
  upper = 0
  right = 0
  lower = 0

  if left == 0:
    factor_x = choice(factors_x)
    factor_y = choice(factors_y)
    if factor_x == 0:
      right = image.size[0]
    else:
      right = image.size[0] * factor_x
    lower = image.size[1] * factor_y;
  else:
    right = image.size[0]
    lower = last_height
  box = (int(left), int(upper), int(right), int(lower))
  return box

def random_move_down(box, space_down):
  move = space_down * random() 
  left = box[0]
  upper = int(box[1] + move)
  right = box[2]
  lower = int(box[3] + move)
  return (left, upper, right, lower)

def drift_box(image, box):
  left = box[2] + 1
  upper = box[1]
  right = image.size[0]
  lower = box[3]
  return (left, upper, right, lower)

def get_scale(out, image):
  scale = float(out.size[0]) / image.size[0]
  return scale

def get_scaled_size(box, scale):
  scaled_width = int((box[2] - box[0]) * scale)
  scaled_height = int((box[3] - box[1]) * scale)
  scaled_size = scaled_width, scaled_height
  return scaled_size

def get_cut(image, box, scaled_size):
  region = image.crop(box).resize(scaled_size)
  return region


def get_drift(box, image):
  if box[2] != image.size[0]:
    return box[2]
  else:
    return 0

if __name__ == '__main__':
  if (len(sys.argv) == 2):
    size_out = sys.argv[0], sys.argv[1]
  analyse()
  load_images()
  out = Image.new("RGB", size_out, color=0)
  v_pointer = 0
  drift = 0
  last_height = 0

  while v_pointer < size_out[1]:
    image = choice(images);
    box = get_region_box(image, drift)
    drift = get_drift(box, image)
    space_down = image.size[1] - box[3]
    #region_size = (box[2], box[3] - box[1])
    last_height = box[3] - box[1]
    box = random_move_down(box, space_down)
    scale = get_scale(out, image)
    scaled_size = get_scaled_size(box, scale)
    region = get_cut(image, box, scaled_size)
    out.paste(region, (box[0], v_pointer))

    while box[2] != image.size[0]:
      image = choice(images)
      box = get_region_box(image, drift, last_height)
      print "second Box: " + str(box)
      drift = get_drift(box, image)
      space_down = image.size[1] - box[3]
      box = random_move_down(box, space_down)
      #box = drift_box(image, box)
      scale = get_scale(out, image)
      scaled_size = get_scaled_size(box, scale)
      print "scaled_size: " + str(scaled_size)
      region = get_cut(image, box, scaled_size)
      print "region_size: " + str(region.size)
      out.paste(region, (int(box[0] * scale), v_pointer))

    v_pointer += scaled_size[1]

  out.save("out.jpg")

  
