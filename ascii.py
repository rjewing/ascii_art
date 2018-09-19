#! /usr/bin/env python
from __future__ import print_function
from PIL import Image
from PIL import ImageOps
from PIL import ImageEnhance
import argparse
import sys

# Define argument parser
parser = argparse.ArgumentParser(description="Convert images into an ASCII image.",
                                 version="1.0.0")
parser.add_argument("file", metavar="FILENAME", help="Path to the file to convert to ASCII.")

parser.add_argument("-s", "--size", nargs=2, type=int, metavar=('WIDTH', 'HEIGHT'), help="Size of output image")
parser.add_argument("-m", "--method", choices=('average', 'lightness', 'luminosity'), default='average', help="Select method to calculate brightness of each pixel.")
parser.add_argument("-c", "--color", action='store_true', help="Prints the ASCII picture in color.")
parser.add_argument("-i", "--invert", action='store_true', help="Inverts the image.")
parser.add_argument("-q", "--quiet", action='store_true', help="Suppress printing of image.")
parser.add_argument("-C", "--characters", choices=('full', 'nums', 'mid', '16bit', '8bit', 'test'), default='mid', help="Select character set to use.")
parser.add_argument("-a", "--adjust", action='store_true', help="Adjust brightness levels so darkest equals 0 and lightest equals 255.")

def getAvg(pixel=(0, 0, 0)):
	return (pixel[0] + pixel[1] + pixel[2]) / 3

def getLightness(pixel=(0, 0, 0)):
	return (max(pixel) + min(pixel)) / 2

def getLuminosity(pixel=(0, 0, 0)):
	return 0.21*pixel[0] + 0.72*pixel[1] + 0.07*pixel[2]

def getASCII(image, method="average", cset='mid', adjust=False):
	ascii_pic = []
	ascii_set = {
		'full': " .'`^\",-~:;!+><i?l][}{1)(|\\/tfjrxnuvczIXYUJCLQ0OZmwqpdbkhao*&8%B$@#MW",
		'nums': " .,'`^/*!1723569059",
		'mid': " .'`^\":;-=+*><]}tfdbO0$@#W",
		'16bit': " .-:!*+=xm%$2#@W",
		'8bit': " .,:ilwW",
		'test': " .\"*:!o%0@#",
	}

	funcs = {
				"average": getAvg,
				"lightness": getLightness,
				"luminosity": getLuminosity,
			}
	chars = ascii_set[cset]

	if adjust:
		min, max = findMinMax(image=image, method=method)
	else:
		min = 0
		max = 255
	print("Min brighntess:", min)
	print("Max brightness:", max)

	for y in range(image.size[1]):
		ascii_row = []
		for x in range(image.size[0]):
			pixel = image.getpixel((x,y))
			val = 255*(funcs[method](pixel) - min)/(max - min)
			# val = funcs[method](pixel)
			ascii_row.append(chars[int((val * (len(chars))-1) / 255)])
		ascii_pic.append(ascii_row)
	return ascii_pic

def getColor(image, invert=False):
	color_pic = []
	for y in range(image.size[1]):
		color_row = []
		for x in range(image.size[0]):
			r, g, b = image.getpixel((x,y))
			color_row.append('\033[38;2;%d;%d;%d;48;2;0;0;0;1m' %(r, g, b))
		color_pic.append(color_row)
	return color_pic

def printASCII(ascii_pic=[], color_pic=[], size=(128, 128)):
	sys.stdout.write("\033[8;%s;%st" %(55, size[0]*2))
	sys.stdout.write("\033[%sB" %(size[1]))
	if color_pic:
		for a_row, c_row in zip(ascii_pic, color_pic):
			print(''.join([b+a+a for a, b in zip(a_row, c_row)])+'\033[0m')
	else:
		for row in ascii_pic:
			print('\033[48;2;0;0;0;1m' + ''.join([c+c for c in row])+'\033[0m')
	# print('\033[0m')

def findMinMax(image, method='average'):
	funcs = {
				"average": getAvg,
				"lightness": getLightness,
				"luminosity": getLuminosity,
			}
	min = 255
	max = 0
	for y in range(image.size[1]):
		for x in range(image.size[0]):
			pixel = image.getpixel((x,y))
			val = funcs[method](pixel)
			if val < min:
					min = val
			if val > max:
				max = val
	return min, max


def main():
	args = parser.parse_args()

	im = Image.open(args.file)
	print("Original size:", im.size)
	print("Resizing...")
	if not args.size:
		args.size = (128, 128)
	im.thumbnail(tuple(args.size))
	print("New size:", im.size)
	print("Processing image...")
	if args.invert:
		im = ImageOps.invert(im)
	ascii_pic = getASCII(image=im, method=args.method, cset=args.characters, adjust=args.adjust)
	color_pic = getColor(image=im) if args.color else None

	if not args.quiet:
		printASCII(ascii_pic, color_pic, args.size)


if __name__ == '__main__':
	main()