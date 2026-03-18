#!/usr/bin/env python3
#   Copyright (c) 2026 Jack Bennett.
#   All Rights Reserved.
#
#   See the LICENCE file for more information.

from PIL import Image, ImageDraw, ImageFont

import argparse
import os
import re

# configure and parse CLI arguments
parser = argparse.ArgumentParser()
parser.add_argument("input",
                    type=str,
                    help="path to the input image")
parser.add_argument("line",
                    type=str,
                    help="line of text to add",
                    nargs="+")
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
parser.add_argument("-s",
                    type=str,
                    help="specify the font size (defaults to 20%% of the " \
                         "image width)",
                    dest="fontsize",
                    default="20%")
args = parser.parse_args()

# validate arguments
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
draw = ImageDraw.Draw(img)

# form text block from specified lines
text = "\n".join(args.line)

# get the input font size as formatted
fontspec_size = 0
fontspec_unit = ""
try:
    fontspec_size, fontspec_unit = \
        re.findall(r"^([0-9.]+)([^0-9\s]*)$", args.fontsize)[0]
except IndexError:
    print(f"Error: invalid/malformed font size specifier \"{args.fontsize}\"")
    exit(1)

fontspec_size = float(fontspec_size)

# font size format validation
if fontspec_unit == "" or fontspec_unit is None:
    print(f"Error: no unit given in font size \"{args.fontsize}\"")
    exit(1)
if fontspec_size < 0.005: # i.e. roughly zero (float)
    print(f"Error: specified font size (\"{args.fontsize}\") cannot be zero")
    exit(1)

# figure out the most ideal actual font size
fontsize = 0
match fontspec_unit:
    # points taken to be absolute value
    case "pt":
        fontsize = fontspec_size

    # percentage fontsize taken to be a proportion of the image width
    case "%":
        _fontprop = fontspec_size * 0.01 # convert percentage to decimal

        # get the font size based on proportion of the image width to take up
        # a method courtesy of Paul on SO:
        # https://stackoverflow.com/a/4902713/12980669
        _imgwid = img.size[0]
        while True:
            fontsize += 1

            # attempt to load font at this size
            try:
                font = ImageFont.truetype(fontpath, fontsize)
            except Exception as e:
                print(f"Error when loading font from {fontpath}: {e}")
                exit(4)

            # get width of rendered text
            _bbox = draw.multiline_textbbox((0, 0), text, font)
            _wid = _bbox[2] - _bbox[0] # right - left

            # repeat with incrementing fontsize until the text is big enough
            if _wid >= _fontprop * _imgwid:
                break

    case _:
        print(f"Invalid unit \"{fontspec_unit}\" specified in font size " \
              f"argument \"{args.fontsize}\"")
        exit(1)

# load the font at the final size
# yes, this is unnecessary when percentage units given, but it isn't too
# expensive soo oh well!
font = ImageFont.truetype(fontpath, fontsize)

draw.text((0, 0), text, font=font,
          stroke_width=fontsize*0.05, stroke_fill="black")

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
