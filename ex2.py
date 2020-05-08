#!/usr/bin/env python3
import numpy as np
import urllib.request
import cv2
import binascii
import lorem
import math
import matplotlib.pyplot as plt


def encode_as_binary_array(msg):
    """Encode a message as a binary string."""
    msg = msg.encode("utf-8")
    msg = msg.hex()
    msg = [msg[i:i + 2] for i in range(0, len(msg), 2)]
    msg = [bin(int(el, base=16))[2:] for el in msg]
    msg = ["0" * (8 - len(el)) + el for el in msg]
    return "".join(msg)


def decode_from_binary_array(array):
    """Decode a binary string to utf8."""
    array = [array[i:i+8] for i in range(0, len(array), 8)]
    if len(array[-1]) != 8:
        array[-1] = array[-1] + "0" * (8 - len(array[-1]))
    array = [hex(int(el, 2))[2:].zfill(2) for el in array]
    array = "".join(array)
    result = binascii.unhexlify(array)
    return result.decode("utf-8", errors="replace")


def hide_message(image, message, nbits=1):
    """Hide a message in an image (LSB).

    nbits: number of least significant bits
    """
    nbits = clamp(nbits, 1, 8)
    shape = image.shape
    image = np.copy(image).flatten()
    if len(message) > len(image) * nbits:
        raise ValueError("Message is to long :(")

    chunks = [message[i:i + nbits] for i in range(0, len(message), nbits)]
    for i, chunk in enumerate(chunks):
        byte = str(bin(image[i]))[2:].zfill(8)
        new_byte = byte[:-nbits] + chunk
        image[i] = int(new_byte, 2)

    return image.reshape(shape)


def clamp(n, minn, maxn):
    """Clamp the n value to be in range (minn, maxn)."""
    return max(min(maxn, n), minn)


def reveal_message(image, nbits=1, length=0):
    """Reveal the hidden message.

    nbits: number of least significant bits
    length: length of the message in bits.
    """
    nbits = clamp(nbits, 1, 8)
    shape = image.shape
    image = np.copy(image).flatten()
    length_in_pixels = math.ceil(length/nbits)
    if len(image) < length_in_pixels or length_in_pixels <= 0:
        length_in_pixels = len(image)

    message = ""
    i = 0
    while i < length_in_pixels:
        byte = str(bin(image[i]))[2:].zfill(8)
        message += byte[-nbits:]
        i += 1

    mod = length % -nbits
    if mod != 0:
        message = message[:mod]
    return message


print("Downloading image!")
path = 'https://picsum.photos/500/500'
resp = urllib.request.urlopen(path)
image = np.asarray(bytearray(resp.read()), dtype="uint8")
image = cv2.imdecode(image, cv2.IMREAD_COLOR)
print("Image downloaded!")


message = lorem.text()*1000
secret = encode_as_binary_array(message)

resultImageRow1 = None
resultImageRow2 = None

nbitsList = range(1, 9)
nbitsMSE = []
for nbits in nbitsList:
    print(nbits)
    imageSecret = hide_message(image, secret[:int(image.size*0.8)], nbits)
    mse = ((imageSecret - image)**2).mean() 
    nbitsMSE.append(mse)

    if nbits <= 4:
        resultImageRow1 = imageSecret if resultImageRow1 is None else np.hstack(
            [resultImageRow1, imageSecret])
    else:
        resultImageRow2 = imageSecret if resultImageRow2 is None else np.hstack(
            [resultImageRow2, imageSecret])



plt.plot(nbitsList, nbitsMSE)
plt.xlabel('nbits')
plt.ylabel('MSE')

cv2.namedWindow("Result", cv2.WINDOW_NORMAL)

cv2.imshow('Result', np.vstack([resultImageRow1, resultImageRow2]))
cv2.imwrite('ex2_encoded.png', np.vstack([resultImageRow1, resultImageRow2]))
cv2.waitKey(1)
plt.savefig('ex2_plot.png')
plt.show()
cv2.waitKey()

# Dla nbits=7,8 MSE zmalał, ponieważ widoczna jest większa część bazowego obrazu 
# - wiadomość zapisano na mniejszej liczbie plkseli