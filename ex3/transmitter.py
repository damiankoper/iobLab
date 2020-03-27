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
    print("Downloading image!")
    path = 'https://picsum.photos/1280/960'
    resp = urllib.request.urlopen(path)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    print("Image downloaded!")
else:
    path = args.i
    image = cv2.imread(path)


ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
y = ycrcb[:, :, 0]
cr = ycrcb[:, :, 1]
cb = ycrcb[:, :, 2]
cv2.namedWindow('Result', cv2.WINDOW_NORMAL)

# 4.0 clockwise real->y->cb->cr
cv2.imshow('Result',
           np.vstack([
               np.hstack(
                   [image, cv2.cvtColor(y, cv2.COLOR_GRAY2BGR)]
               ),
               np.hstack(
                   [cv2.cvtColor(cb, cv2.COLOR_GRAY2BGR),
                    cv2.cvtColor(cr, cv2.COLOR_GRAY2BGR)]
               )
           ])
           )
cv2.waitKey()

compression = 8
baseShape = cr.shape[::-1]
smallShape = (int(baseShape[0]/compression),
              int(baseShape[1]/compression))
# Coder
cr = cv2.resize(cr, smallShape, interpolation=cv2.INTER_LINEAR)
cb = cv2.resize(cb, smallShape, interpolation=cv2.INTER_LINEAR)

# Decoder
cr = cv2.resize(cr, baseShape, interpolation=cv2.INTER_LINEAR)
cb = cv2.resize(cb, baseShape, interpolation=cv2.INTER_LINEAR)

ycrcb[:, :, 1] = cr
ycrcb[:, :, 2] = cb

newImage = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
cv2.imshow('Result',
           np.vstack([
               np.hstack(
                   [cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR),
                    cv2.cvtColor(y, cv2.COLOR_GRAY2BGR)]
               ),
               np.hstack(
                   [cv2.cvtColor(cb, cv2.COLOR_GRAY2BGR),
                    cv2.cvtColor(cr, cv2.COLOR_GRAY2BGR)]
               )
           ])
           )
mse = ((image - newImage)**2).mean()
print(f"MSE with compression x{compression}: {mse}")

cv2.waitKey()
