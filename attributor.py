#!/usr/bin/env python3
#   Copyright (c) 2026 Jack Bennett.
#   All Rights Reserved.
#
#   See the LICENCE file for more information.

from PIL import Image, ImageDraw

import argparse

# configure and parse CLI arguments
parser = argparse.ArgumentParser()
parser.add_argument("input",
                    type=str,
                    help="path to the input image")
parser.add_argument("-o",
                    type=str,
                    help="path to the output image",
                    dest="output")
parser.add_argument("-i",
                    action="store_true",
                    help="edit the image in-place",
                    dest="inplace")
parser.add_argument("-f",
                    type=str,
                    help="set the font used for added text",
                    choices=["dos"],
                    dest="font",
                    default="dos")
args = parser.parse_args()

# validate conditionally required arguments
if args.inplace and args.output is not None:
    parser.error("The flags -o and -i cannot be used simultaneously")
    exit(1)

# if no output path given (and not editing in-place), then preview instead
preview = False
if not args.inplace and args.output is None:
    preview = True

basepath = os.path.dirname(os.path.realpath(__file__))
fontpath = os.path.join(basepath, "fonts", f"{args.font}.ttf")

# attempt to read input image
try:
    img = Image.open(args.input, "r")
except Exception as e:
    print(f"Error when loading image at {args.input}: {e}")
    exit(2)

font = ImageFont.truetype(fontpath, 30)

# draw text to image
draw = ImageDraw.Draw(img)

draw.text((0, 0), "jerma985", font=font)

# if just previewing the output, then show the image and exit cleanly
if preview:
    img.show()
    img.close()
    exit(0)

# output image to args.output if given, or args.input if not (i.e. if -i was
# specified)
outpath = args.output or args.input
try:
    img.save(outpath)
except Exception as e:
    print(f"Error when saving image to {outpath}: {e}")
    exit(3)

img.close()
