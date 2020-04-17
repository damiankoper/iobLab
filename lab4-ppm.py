#!/usr/bin/env python3
import numpy as np
import urllib.request
import cv2


print("Downloading image!")
path = 'https://picsum.photos/1280/960'
resp = urllib.request.urlopen(path)
image = np.asarray(bytearray(resp.read()), dtype="uint8")
image = cv2.imdecode(image, cv2.IMREAD_COLOR)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
print("Image downloaded!")
shape = image.shape

# PPM file header
ppm_ascii_header = 'P3 ' + str(shape[1]) + ' ' + str(shape[0]) + ' 255 '
ppm_binary_header = 'P6 ' + str(shape[1]) + ' ' +  str(shape[0]) + ' 255 '

# Image data
image = np.array(image.flatten(), dtype=np.uint8)

# Save the PPM image as an ASCII file
with open('lab4-ascii.ppm', 'w') as fh:
    fh.write(ppm_ascii_header) 
    image.tofile(fh, ' ')

# Save the PPM image as a binary file
with open('lab4-binary.ppm', 'wb') as fh:
    fh.write(bytearray(ppm_binary_header, 'ascii'))
    image.tofile(fh)


# Format binarny naturalnie jest mniejszy niż tekstowy z racji na
# narzut jaki stanowią białe znaki i kodowanie każdej cyfry w ascii