import cv2
import numpy as np
import argparse
import urllib.request

parser = argparse.ArgumentParser(
    description="Pixel transform.")
picsum = parser.add_mutually_exclusive_group()
file = parser.add_mutually_exclusive_group()
picsum.add_argument(
    '-p', help="input image from picsum.photos", action='store_true')
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

m = [
    [0.393, 0.769, 0.189],
    [0.349, 0.689, 0.168],
    [0.272, 0.534, 0.131],
]
m = np.asarray(m)
modified = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
modified = np.rint(modified.dot(m.T)).astype('uint8')


cv2.namedWindow('Result', cv2.WINDOW_NORMAL)

cv2.imshow('Result', np.hstack([image, modified]))
cv2.waitKey()
