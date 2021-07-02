# ASCII encoding for Piet

A way of encoding [Piet](https://esolangs.org/wiki/Piet) programs in ASCII text files, one character per codel.

## Usage

To convert an ASCII-encoded file `prog.txt` into a PNG image `prog.png`:

    python3 ascii2piet.py prog.txt prog.png

If the filenames are omitted, the converter reads input from stdin and sends output to stdout. To type ASCII-encoded Piet directly at the command-line and save the output image in `prog.png`:

    python3 ascii2piet.py > prog.png

The `-s` or `--size` flag specifies the codel size: with `-s 10`, each codel will be represented in the output image by a 10x10 square of pixels. The default codel size is 1. 

The `-x` or `--xxd` flag outputs an xxd-style hexdump of a PNG image instead of raw bytes.

The `-v` or `--verbose` flag outputs more information on the conversion process to stderr.

## Encoding specification

Each of Piet's 20 colors is associated with two ASCII characters: one for when the codel appears at the end of a row, and one for all other occurrences.

Color         | Char | End-of-line char
--------------|------|-----------------
Black         | <code>&nbsp;</code> | `@`
Dark blue     | `a`  | `A`
Dark green    | `b`  | `B`
Dark cyan     | `c`  | `C`
Dark red      | `d`  | `D`
Dark magenta  | `e`  | `E`
Dark yellow   | `f`  | `F`
Blue          | `i`  | `I`
Green         | `j`  | `J`
Cyan          | `k`  | `K`
Red           | `l`  | `L`
Magenta       | `m`  | `M`
Yellow        | `n`  | `N`
Light blue    | `q`  | `Q`
Light green   | `r`  | `R`
Light cyan    | `s`  | `S`
Light red     | `t`  | `T`
Light magenta | `u`  | `U`
Light yellow  | `v`  | `V`
White         | `?`  | `_`

If any lines are shorter than the longest line, the translator right-pads them with black codels. Thus, black codels at the ends of lines may be omitted.

## Example

Consider the following Piet program by StackExchange user [plannapus](https://codegolf.stackexchange.com/users/6741/plannapus), which prints the number 42 forever:

<a href="https://codegolf.stackexchange.com/a/22977/16766"><img src="https://i.stack.imgur.com/6hZwO.png" alt="Piet program to print 42 forever" /></a>

It contains 18 codels and uses the colors red, dark red, black, light red, and dark yellow. Ignoring the encoding of newlines for the moment, the ASCII equivalent of these codels is:

    lldd  
    lldddt
    llddtf

We then change the codels in the final column to their end-of-line versions:

    lldd @
    lldddT
    llddtF

Finally, we remove the newlines for an 18-byte encoded file:

    lldd @lldddTllddtF

However, the first row ends with two black codels, which we can omit if we mark the last dark red codel on the line as the end-of-line instead. This approach gives us a 16-byte encoded file:

    lldDlldddTllddtF

Either file will decode correctly into the original image.
