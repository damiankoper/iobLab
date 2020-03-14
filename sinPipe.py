import argparse
import sys
import io
import math
import os

"""
Jeśli nie dostarczono argumentu -i to input brany jest z klawiatury, a wyniki zapisywane do pliku.
"""

parser = argparse.ArgumentParser(
    description="Calc sin function. If input or output paths are not provided stdin and stdout are used.")
parser.add_argument('-i', help="input file's relative path", metavar="path")
parser.add_argument('-o', help="input file's relative path", metavar="path")
args = parser.parse_args()


if args.i is None:
    inputStream = sys.stdin
else:
    inputStream = io.open(args.i, 'r')

if args.o is None:
    outputStream = sys.stdout
else:
    outputStream = io.open(args.o, 'w')

value = inputStream.readline().strip()
while value:
    outputStream.write(str(math.sin(float(value))) + os.linesep)
    value = inputStream.readline()
# 4.0 done