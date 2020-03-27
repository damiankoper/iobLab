import cv2
import numpy as np
import argparse
import urllib.request

parser = argparse.ArgumentParser(
    description="Edge detector.")
picsum = parser.add_mutually_exclusive_group()
file = parser.add_mutually_exclusive_group()
picsum.add_argument('-p', help="input image from picsum.photos", action='store_true')
file.add_argument('-i', help="input image relative path", metavar="path")
args = parser.parse_args()

if args.p is True:
    path = 'https://picsum.photos/1280/960'
    resp = urllib.request.urlopen(path)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
else:
    path = args.i
    image = cv2.imread(path)

kernel = [
    [-1, -1, -1],
    [-1, 8, -1],
    [-1, -1, -1],
]
kernel = np.asarray(kernel)
edges = cv2.filter2D(image,-1,kernel)
cv2.namedWindow('Result',cv2.WINDOW_NORMAL)
cv2.imshow('Result', np.hstack([image,edges]))
cv2.waitKey()