#!/usr/bin/env python3
import numpy as np
import urllib.request
import cv2
import binascii
import lorem
import math


def encode_as_binary_array(msg):
    """Encode a message as a binary string."""
    msg = msg.encode("utf-8")
    msg = msg.hex()
    msg = [msg[i:i + 2] for i in range(0, len(msg), 2)]
    msg = [bin(int(el, base=16))[2:] for el in msg]
    msg = ["0" * (8 - len(el)) + el for el in msg]
    return "".join(msg)


def clamp(n, minn, maxn):
    """Clamp the n value to be in range (minn, maxn)."""
    return max(min(maxn, n), minn)


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


def reveal_message(image, nbits=1):
    """Reveal the hidden message.

    nbits: number of least significant bits
    length: length of the message in bits.
    """
    nbits = clamp(nbits, 1, 8)
    shape = image.shape
    image = np.copy(image).flatten()
    length_in_pixels = len(image)

    message = ""
    i = 0
    while i < length_in_pixels:
        byte = str(bin(image[i]))[2:].zfill(8)
        message += byte[-nbits:]
        i += 1

    return message


def hide_image(image, secret_image_path, nbits=1):
    with open(secret_image_path, "rb") as file:
        secret_img = file.read()

    secret_img = secret_img.hex()
    secret_img = [secret_img[i:i + 2] for i in range(0, len(secret_img), 2)]
    secret_img = [bin(int(el, base=16))[2:].zfill(8) for el in secret_img]
    secret_img = "".join(secret_img)
    return hide_message(image, secret_img, nbits), len(secret_img)


def reveal_image(image, secret_image_path, nbits=1):
    decoded = reveal_message(image, nbits)
    footerPart = encode_as_binary_array("IEND")
    position = decoded.find(footerPart) + 32 + 32 + 8 # Footer id + CRC32
    # Nie trzeba dokładnie zapisać długości, można w ogóle nie obcinać. Ważne, żeby nie obciąć CRC.

    with open(secret_image_path, "wb") as file:
        cur = 0
        while cur < position:
            c = int(decoded[cur:cur+8], 2)
            file.write(bytes(chr(c), 'iso8859-1'))
            cur += 8


print("Downloading images!")
path = 'https://picsum.photos/500/500'
resp = urllib.request.urlopen(path)
imageSecret = np.asarray(bytearray(resp.read()), dtype="uint8")
imageSecret = cv2.imdecode(imageSecret, cv2.IMREAD_COLOR)
cv2.imwrite('ex4_5_secret.png', imageSecret)

path = 'https://picsum.photos/1280/960'
resp = urllib.request.urlopen(path)
image = np.asarray(bytearray(resp.read()), dtype="uint8")
image = cv2.imdecode(image, cv2.IMREAD_COLOR)
print("Images downloaded!")

nbits = 5

image, length_secret = hide_image(image, 'ex4_5_secret.png', nbits)
reveal_image(image, 'ex4_5_secret_decoded.png', nbits)


cv2.imwrite('ex4_5_result.png', image)
cv2.imshow('Result', image)
cv2.waitKey()
