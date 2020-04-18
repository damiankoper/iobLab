#!/usr/bin/env python3
import numpy
import lab4_utils
import numpy as np
import zlib
import cv2

# Nie ma co kombinować :)
# https://github.com/lot9s/lfv-compression/blob/master/scripts/our_mpeg/zigzag.py
zigzag = np.array([[0,  1,  5,  6,  14, 15, 27, 28],
                   [2,  4,  7,  13, 16, 26, 29, 42],
                   [3,  8,  12, 17, 25, 30, 41, 43],
                   [9,  11, 18, 24, 31, 40, 44, 53],
                   [10, 19, 23, 32, 39, 45, 52, 54],
                   [20, 22, 33, 38, 46, 51, 55, 60],
                   [21, 34, 37, 47, 50, 56, 59, 61],
                   [35, 36, 48, 49, 57, 58, 62, 63]])
zigzagFlatten = zigzag.flatten()
zigzagIndexes = np.argsort(zigzagFlatten)

# 0. Image data
# Params
width = 256 * 7
height = 50
compression = 2
QF = 10
interpolation = cv2.INTER_LINEAR

up = np.arange(0, 256, dtype=np.uint8)
down = np.arange(255, -1, -1, dtype=np.uint8)
zero = np.full(256, 0, dtype=np.uint8)
full = np.full(256, 255, dtype=np.uint8)

transition1 = np.array([zero, zero, up])
transition2 = np.array([zero, up, full])
transition3 = np.array([zero, full, down])
transition4 = np.array([up, full, zero])
transition5 = np.array([full, down, zero])
transition6 = np.array([full, zero, up])
transition7 = np.array([full, up, full])

imageRow = np.concatenate((
    transition1.transpose(),
    transition2.transpose(),
    transition3.transpose(),
    transition4.transpose(),
    transition5.transpose(),
    transition6.transpose(),
    transition7.transpose(),
), axis=0)

image = np.reshape(np.tile(imageRow.flatten(), height), (height, width, 3))

# 1. Convert RGB to YCbCr
ycrcb = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
y = ycrcb[:, :, 0]
cr = ycrcb[:, :, 1]
cb = ycrcb[:, :, 2]

# 2. Downsampling on Cb Cr
baseShape = cr.shape[::-1]
smallShape = (int(baseShape[0]/compression),
              int(baseShape[1]/compression))
cr = cv2.resize(cr, smallShape, interpolation=interpolation)
cb = cv2.resize(cb, smallShape, interpolation=interpolation)

# 3. Produce 8x8 blocks


def produce_8(matrix):
    size = 8
    blocks = []

    for h in range(0, matrix.shape[0], 8):
        for w in range(0, matrix.shape[1], 8):
            block = matrix[h:h+8, w:w+8]
            block = np.pad(
                block, ((0, 8-block.shape[0]), (0, 8-block.shape[1])), constant_values=np.mean(block))
            blocks.append(block)

    return blocks


y_blocks = produce_8(y)
cr_blocks = produce_8(cr)
cb_blocks = produce_8(cb)

# 4. Calculate DCT on each block
for (i, block) in enumerate(y_blocks):
    y_blocks[i] = lab4_utils.dct2(block)
for (i, block) in enumerate(cr_blocks):
    cr_blocks[i] = lab4_utils.dct2(block)
for (i, block) in enumerate(cb_blocks):
    cb_blocks[i] = lab4_utils.dct2(block)

# 5. Divide each block by quantisation matrix
# 6. Round each block to integers
QY = lab4_utils.QY(QF)
QC = lab4_utils.QC(QF)
for (i, block) in enumerate(y_blocks):
    y_blocks[i] = np.round(np.divide(block, QY)).astype(np.int)
for (i, block) in enumerate(cr_blocks):
    cr_blocks[i] = np.round(np.divide(block, QC)).astype(np.int)
for (i, block) in enumerate(cb_blocks):
    cb_blocks[i] = np.round(np.divide(block, QC)).astype(np.int)

# 7. Zig Zag
for (i, block) in enumerate(y_blocks):
    y_blocks[i] = np.array(block.flatten()[zigzagIndexes])
for (i, block) in enumerate(cr_blocks):
    cr_blocks[i] = np.array(block.flatten()[zigzagIndexes])
for (i, block) in enumerate(cb_blocks):
    cb_blocks[i] = np.array(block.flatten()[zigzagIndexes])

# 8. Flatten, concatenate, compress and calculate the size -- how many bytes?
data = np.concatenate((
    np.array(y_blocks).flatten(),
    np.array(cr_blocks).flatten(),
    np.array(cb_blocks).flatten()
))
data = zlib.compress(data)
print(len(data))

# 7'. Undo Zig Zag
for (i, block) in enumerate(y_blocks):
    y_blocks[i] = np.array(block[zigzagFlatten]).reshape((8, 8))
for (i, block) in enumerate(cr_blocks):
    cr_blocks[i] = np.array(block[zigzagFlatten]).reshape((8, 8))
for (i, block) in enumerate(cb_blocks):
    cb_blocks[i] = np.array(block[zigzagFlatten]).reshape((8, 8))

# 6'. Nothing to do here   ¯\_(ツ)_/¯
# 5'. Reverse division by quantisation matrix -- multiply
for (i, block) in enumerate(y_blocks):
    y_blocks[i] = np.multiply(block, QY)
for (i, block) in enumerate(cr_blocks):
    cr_blocks[i] = np.multiply(block, QC)
for (i, block) in enumerate(cb_blocks):
    cb_blocks[i] = np.multiply(block, QC)
# 4'. Reverse DCT
for (i, block) in enumerate(y_blocks):
    y_blocks[i] = lab4_utils.idct2(block)
for (i, block) in enumerate(cr_blocks):
    cr_blocks[i] = lab4_utils.idct2(block)
for (i, block) in enumerate(cb_blocks):
    cb_blocks[i] = lab4_utils.idct2(block)

# 3'. Combine 8x8 blocks to original image


def combine_8(blocks, shape):
    m_width = shape[1]//8+1 if shape[1] % 8 != 0 else shape[1]//8
    m_height = shape[0]//8+1 if shape[0] % 8 != 0 else shape[0]//8

    matrix = None
    for h in range(0, m_height):
        row = None
        for w in range(0, m_width):
            block = blocks[h*m_width+w]
            if row is None:
                row = block
            else:
                row = np.hstack([row, block])
        if matrix is None:
            matrix = row
        else:
            matrix = np.vstack([matrix, row])

    return matrix


y = combine_8(y_blocks, (height, width))[0:height, 0:width]
cr = combine_8(cr_blocks, smallShape[::-1])[0:smallShape[1], 0:smallShape[0]]
cb = combine_8(cb_blocks, smallShape[::-1])[0:smallShape[1], 0:smallShape[0]]


# 2'. Upsampling on Cb Cr
cr = cv2.resize(cr, baseShape, interpolation=interpolation)
cb = cv2.resize(cb, baseShape, interpolation=interpolation)

# 1'. Convert YCbCr to RGB
ycrcb_new = np.copy(ycrcb)
ycrcb_new[:, :, 0] = y
ycrcb_new[:, :, 1] = cr
ycrcb_new[:, :, 2] = cb

# 0'. Save the decoded newImage -- as PPM or PNG
newImage = cv2.cvtColor(ycrcb_new, cv2.COLOR_YCrCb2BGR)
cv2.imshow("DECOMPRESSED", newImage)
cv2.imwrite("decompressed_jpeg.png", newImage) 

mse = ((ycrcb - ycrcb_new)**2).mean()
print(f"MSE with compression x{compression}: {mse}")

cv2.waitKey()

"""
Bez próbkowania:
Rozmiar: 38916
MSE (interpolacja liniowa): 0.481108
MSE (najbliższy): 0.481108

Próbkowanie co 2:
Rozmiar: 23049
MSE (interpolacja liniowa): 0.375386
MSE (najbliższy): 0.595837

Próbkowanie co 4:
Rozmiar: 16842
MSE (interpolacja liniowa): 0.606480
MSE (najbliższy): 0.910807

W przypadku tęczy upsampling z zastosowaną interpolacją (i bez) nie zmienia wyglądu obrazu prawie wcale.
Płynne przejścia kolorów ułatwiają ich odtworzenie z wykorzystaniem interpolacji liniowej.
Rozmiar danych po kompresji zmniejsza się jednak znacząco.


####

Czynnik QF(próbkowanie co 2, interpolacja liniowa)
99:
Rozmiar: 23049
MSE: 0.375386

70:
Rozmiar: 11588
MSE: 0.626856


40:
Roamiar: 10325
MSE: 1.300803

10:
Roamiar: 6778
MSE: 10.453489

Zmniejszenie liczby poziomów kwantyzacji zmniejsza rozmiar danych po kompresji.
Obraz po odtworzeniu, dla coraz mniejszego QF jest coraz bardziej zdegradowany. Widać przejścia pomiędzy kolorami.
"""