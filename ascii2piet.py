#!/usr/bin/python3

import sys
import io
import argparse

try:
    from PIL import Image
except ImportError:
    print("Pillow module must be installed", file=sys.stderr)
    raise


HUE_MASK = 0b111
BLACK = 0b000
BLUE = 0b001
GREEN = 0b010
RED = 0b100
WHITE = 0b111

LIGHTNESS_MASK = 0b11000
DARK = 0b00000
NORMAL = 0b01000
LIGHT = 0b10000

NO_EOL_MASK = 0b100000


def encode_newlines(ascii_piet):
    "Encode newlines into the end-of-line bit of the previous char."
    ascii_lines = ascii_piet.splitlines()
    encoded_lines = []
    for line in ascii_lines:
        if line:
            # Turn the codel at the end of each line into its EOL
            # equivalent
            last_charcode = ord(line[-1])
            last_charcode &= ~NO_EOL_MASK
            # If the mask took the charcode out of printable range,
            # shift it back into printable range
            if last_charcode < 32:
                last_charcode += 64
            encoded_char = chr(last_charcode)
            encoded_lines.append(line[:-1] + encoded_char)
    return "".join(encoded_lines)


def decode_newlines(ascii_piet):
    "Decode the end-of-line bit into actual newlines."
    piet_with_newlines = ""
    for char in ascii_piet:
        if char == "\n":
            # There shouldn't be any newlines in the encoded version
            # before this function adds them
            continue
        charcode = ord(char)
        if charcode & NO_EOL_MASK:
            # A codel that is not at end of line gets passed through
            # unchanged
            piet_with_newlines += char
        else:
            # A codel that is at end of line gets turned into its
            # no-EOL equivalent and a newline appended
            piet_with_newlines += chr(charcode | NO_EOL_MASK) + "\n"
    # Return the new code with trailing newlines removed
    return piet_with_newlines.rstrip("\n")


def ascii_to_image(ascii_piet, codel_size, verbose=False):
    "Convert ASCII-encoded Piet into a PIL Image object."
    # Make sure any literal newlines in the input are encoded into the
    # EOL bits
    ascii_piet = encode_newlines(ascii_piet)
    if verbose:
        print_stderr("ASCII-encoded Piet is", len(ascii_piet), "bytes:")
        print_stderr(ascii_piet)
        print_stderr()
    # Then turn them back into literal newlines
    ascii_piet = decode_newlines(ascii_piet)
    if verbose:
        print_stderr("With newlines added:")
        print_stderr(ascii_piet)
        print_stderr()
    ascii_lines = ascii_piet.splitlines()
    image_width = max(len(line) for line in ascii_lines)
    image_height = len(ascii_lines)
    if verbose:
        print_stderr(f"Program size is {image_width} by {image_height}",
                     f"({image_width*image_height} codels)")
    # Pad short lines with spaces (black codels)
    ascii_lines = [line.ljust(image_width, " ") for line in ascii_lines]
    codels = []
    for line in ascii_lines:
        for char in line:
            charcode = ord(char)
            hue = charcode & HUE_MASK
            lightness = charcode & LIGHTNESS_MASK
            if hue == WHITE or hue == BLACK:
                # White and black don't come in light/dark variants
                lightness = NORMAL
            if lightness == DARK:
                intensities = (0, 192)
            elif lightness == NORMAL:
                intensities = (0, 255)
            elif lightness == LIGHT:
                intensities = (192, 255)
            isred = bool(hue & RED)
            isgreen = bool(hue & GREEN)
            isblue = bool(hue & BLUE)
            rgb = (intensities[isred],
                   intensities[isgreen],
                   intensities[isblue])
            codels.append(rgb)
    img = Image.new("RGB", (image_width, image_height))
    img.putdata(codels)
    # Scale the image up by a factor equal to codel_size
    if verbose:
        print_stderr("Generating image with codel size", codel_size)
        print_stderr()
    real_width = image_width * codel_size
    real_height = image_height * codel_size
    img = img.resize((real_width, real_height), resample=Image.NEAREST)
    return img


def padded_hex(num, width=0):
    "Convert to hexadecimal and left-pad with zeros to width."
    hex_num = hex(num)[2:]
    if width > 0:
        hex_num = hex_num.rjust(width, "0")
    return hex_num


def xxd(bytestring):
    "Return xxd-style hexdump of bytestring."
    hexdump = ""
    i = 0
    while i < len(bytestring):
        hexdump += padded_hex(i, 8) + ": "
        block = bytestring[i:i+16]
        hexcodes = ""
        for j in range(0, 16, 2):
            hexcodes += "".join(padded_hex(b, 2) for b in block[j:j+2]) + " "
        hexdump += hexcodes.ljust(40)
        hexdump += " " + "".join(chr(b) if 32 <= b <= 126 else "."
                                 for b in block)
        hexdump += "\n"
        i += 16
    return hexdump.rstrip()


def positive_int(string):
    "Convert string to integer; raise ValueError if not positive."
    val = int(string)
    if val <= 0:
        raise ValueError("must be an integer greater than 0")
    return val


def print_stderr(*args):
    "Print values to stderr."
    print(*args, file=sys.stderr)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-s", "--size", default=1, type=positive_int,
                           help="Output an image with the given codel size",
                           metavar="CODEL_SIZE")
    argparser.add_argument("-x", "--xxd", action="store_true",
                           help="Output as xxd hexdump instead of raw bytes")
    argparser.add_argument("-v", "--verbose", action="store_true",
                           help="Output extra information about the Piet "
                           "program to stderr")
    argparser.add_argument("infile", nargs="?", default=None,
                           help="Source file for ASCII-encoded input "
                           "(default: read from stdin)")
    argparser.add_argument("outfile", nargs="?", default=None,
                           help="Destination file for PNG output "
                           "(default: dump to stdout)")
    options = argparser.parse_args()
    if options.verbose:
        print_stderr("Converting from ASCII-encoded Piet to PNG")
        if options.infile is not None:
            print_stderr("Source file:", options.infile)
        else:
            print_stderr("Source file: <stdin>")
        if options.outfile is not None:
            print_stderr("Destination file:", options.outfile)
        else:
            print_stderr("Destination file: <stdout>")
        print_stderr()
    if options.infile is not None:
        try:
            with open(options.infile) as f:
                ascii_piet = f.read()
        except:
            print_stderr("Could not read from", options.infile)
            raise
    else:
        # If no infile was provided, read from stdin
        ascii_piet = sys.stdin.read()
    img = ascii_to_image(ascii_piet, options.size, verbose=options.verbose)
    if options.xxd:
        # Dump the image in xxd format to the specified output
        if options.verbose:
            print_stderr("Outputting PNG file as hexdump")
        bytestream = io.BytesIO()
        img.save(bytestream, "PNG")
        hexdump = xxd(bytestream.getvalue())
        if options.outfile is not None:
            with open(options.outfile, 'w') as f:
                f.write(hexdump)
        else:
            print(hexdump)
    else:
        if options.verbose:
            print_stderr("Outputting PNG file as raw bytes")
        if options.outfile is not None:
            # Save the image as a PNG to the provided file
            img.save(options.outfile, "PNG")
        else:
            # If no file was given, dump raw image data to stdout
            img.save(sys.stdout.buffer, "PNG")

