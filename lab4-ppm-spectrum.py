#!/usr/bin/env python3
import numpy as np
import urllib.request
import cv2


width = 256 * 7
height = 50

up = np.arange(0,256, dtype=np.uint8)
down = np.arange(255,-1,-1, dtype=np.uint8)
zero = np.full(256, 0, dtype=np.uint8)
full = np.full(256, 255, dtype=np.uint8)

transition1 = np.array([zero, zero, up])
transition2 = np.array([zero, up, full])
transition3 = np.array([zero, full, down])
transition4 = np.array([up, full, zero])
transition5 = np.array([full, down, zero])
transition6 = np.array([full, zero, up])
transition7 = np.array([full, up, full])

image = np.concatenate((
    transition1.transpose(),
    transition2.transpose(),
    transition3.transpose(),
    transition4.transpose(),
    transition5.transpose(),
    transition6.transpose(),
    transition7.transpose(),
),axis=0)

# PPM file header
ppm_ascii_header = 'P3 ' + str(width) + ' ' + str(height) + ' 255 '
ppm_binary_header = 'P6 ' + str(width) + ' ' + str(height) + ' 255 '

# Image data
image = np.array(np.tile(image.flatten(), height), dtype=np.uint8)
#image = np.array(image.flatten(), dtype=np.uint8)

# Save the PPM image as an ASCII file
with open('lab4-ascii-spec.ppm', 'w') as fh:
    fh.write(ppm_ascii_header)
    image.tofile(fh, ' ')

# Save the PPM image as a binary file
with open('lab4-binary-spec.ppm', 'wb') as fh:
    fh.write(bytearray(ppm_binary_header, 'ascii'))
    image.tofile(fh)
