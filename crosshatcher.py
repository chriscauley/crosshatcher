#!/usr/bin/python
#
#       Copyright (C) 2013 Stephen M. Cameron
#       Author: Stephen M. Cameron
#
#       This file is part of crosshatcher.
#
#       crosshatcher is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       crosshatcher is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with crosshatcher; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

import pygame
import time
import os, sys
from PIL import Image
import random
import math
import time
import liangbarsky

imagename = "image.jpg";
if (len(sys.argv) >= 2):
  imagename = sys.argv[1];

parts  = imagename.split('.')
outname = 'output/'+'.'.join(parts[:-1])+'_out.png'

im = Image.open(imagename)
im = im.convert("L")
im.save("gray.png")

pix = im.load()
image_width = 0.0 + im.size[0];
image_height = 0.0 + im.size[1];
screen_width = 3000 
screen_height = int(screen_width * image_height / image_width);
print image_width, image_height, screen_width, screen_height

# origin on screen
osx = 0;
osy = 0;

black = (0, 0, 0)
white = (255, 255, 255)
nlayers = 10;
linespacing = 30;

try:
  os.mkdir('output')
except OSError:
  pass

myfile = open('lines.txt', 'w+');

radius = math.sqrt(2.0) * (1.1 * screen_height);

if screen_width > screen_height:
   radius = math.sqrt(2.0) * (1.1 * screen_width)

screen = pygame.display.set_mode([screen_width, screen_height])
pygame.display.update()

# screen x to image x
def sxtoix(sx):
  return (image_width * sx) / screen_width;

def sytoiy(sy):
  return (image_height * sy) / screen_height;

def sampleimg(sx, sy):
   ix = sxtoix(sx)
   iy = sytoiy(sy)
   if ix < 0:
      return 0
   if iy < 0:
      return 0
   if ix >= image_width:
      return 0
   if iy >= image_height:
      return 0
   return pix[ix, iy]

def rotate_point(p, c, angle):
   x = p[0];
   y = p[1];
   cx = c[0];
   cy = c[1];
   rx = (x - cx) * math.cos(angle) - (y - cy) * math.sin(angle);
   ry = (x - cx) * math.sin(angle) + (y - cy) * math.cos(angle);
   return (rx + cx, ry + cy);

def hypot(p1, p2):
   return math.sqrt((p1[0] - p2[0]) * (p1[0] - p2[0]) +
			(p1[1] - p2[1]) * (p1[1] - p2[1]));

def do_a_line(threshold, p1, p2):
   d = hypot(p1, p2);
   seglen = linespacing;
   nsegs = int(d / seglen);
   pendown = 0;

   dx = (p2[0] - p1[0]) / nsegs;
   dy = (p2[1] - p1[1]) / nsegs;
   for i in range(0, nsegs - 1):
      x1 = p1[0] + dx * i;
      y1 = p1[1] + dy * i;
      x2 = p1[0] + dx * (i + 1);
      y2 = p1[1] + dy * (i + 1);
      mx = ((x2 - x1) / 2.0) + x1;
      my = ((y2 - y1) / 2.0) + y1;
      s = sampleimg(mx, my);
      if s <= threshold:
         if pendown != 1:
            pendown = 1;
            print >> myfile, "start line ", x1, y1
         pygame.draw.line(screen, black, (x1, y1), (x2, y2), 1);
      else:
         if pendown == 1:
            pendown = 0;
            print >> myfile, "end line ", x1, y1;

      if pendown == 1:
            pendown = 0;
            print >> myfile, "end line ", x1, y1;

def do_layer(layer, threshold, angle):
   count = int((radius * 2.0) / linespacing);
   cx = screen_width / 2.0;
   cy = screen_height / 2.0;
   for i in range(-count / 2, count / 2):
      x1 = cx + (i * linespacing);
      y1 = cy - radius * 2;
      x2 = x1;
      y2 = cy + radius * 2;
      p1 = rotate_point((x1, y1), (cx, cy), angle);
      p2 = rotate_point((x2, y2), (cx, cy), angle); 

      clipped_line = liangbarsky.liangbarsky(0, 0, screen_width, screen_height, p1[0], p1[1], p2[0], p2[1]);
      if (clipped_line[0] is None):
         continue;
      p1 = (clipped_line[0], clipped_line[1])
      p2 = (clipped_line[2], clipped_line[3])
      do_a_line(threshold, p1, p2);
      pygame.display.update()

screen.fill(white)
for i in range(1, nlayers):
   do_layer(i, i * 256 / nlayers, i * 127 * math.pi / 180.0);

myfile.close();

pygame.image.save(screen, outname)
print
print
print "Saved output image to %s"%outname
print
print

