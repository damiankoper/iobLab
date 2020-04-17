#!/usr/bin/env python3
import numpy as np
import struct
import zlib

width = 256 * 7
height = 50

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

imageFlat = np.tile(np.insert(imageRow.flatten(), 0, 0), height)

# Construct signature
png_file_signature = b'\x89PNG\r\n\x1a\n'

# Construct header
header_id = b'IHDR'
header_content = struct.pack('!IIBBBBB', width, height, 8, 2, 0, 0, 0)
header_size = struct.pack('!I', len(header_content))
header_crc = struct.pack('!I', zlib.crc32(header_id + header_content))
png_file_header = header_size + header_id + header_content + header_crc

# Construct data
data_id = b'IDAT'
data_content = zlib.compress(imageFlat)
data_size = struct.pack('!I', len(data_content))
data_crc = struct.pack('!I', zlib.crc32(data_id + data_content))
png_file_data = data_size + data_id + data_content + data_crc

# Consruct end
end_id = b'IEND'
end_content = b''
end_size = struct.pack('!I', len(end_content))
end_crc = struct.pack('!I', zlib.crc32(end_id + end_content))
png_file_end = end_size + end_id + end_content + end_crc

# Save the PNG image as a binary file
with open('lab4.png', 'wb') as fh:
    fh.write(png_file_signature)
    fh.write(png_file_header)
    fh.write(png_file_data)
    fh.write(png_file_end)
