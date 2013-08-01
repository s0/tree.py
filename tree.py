#! /usr/bin/env python

"""
Tree.py: Tree is a small utility that displays input from stdin in a tree-like
structure

Copyright © 2013 Sam Lanning <sam@samlanning.com>
This work is free. You can redistribute it and/or modify it under the
terms of the Do What The Fuck You Want To Public License, Version 2,
as published by Sam Hocevar. See the COPYING file for more details.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://www.wtfpl.net/ for more details.

"""


import argparse
import collections
import fileinput
import os
import sys


## Modes

# The different modes of parsing that tree.py can handle
class ParsingMode:
    NoInput, Normal, Grep = range(3)

# Map from command-line flags to actual values in ParsingMode
map_mode = {
    'none': ParsingMode.NoInput,
    'normal': ParsingMode.Normal,
    'n': ParsingMode.Normal,
    'grep': ParsingMode.Grep,
    'g': ParsingMode.Grep
}


## Colors

# Will color be used or not?
class ColorMode:
    NoColor, Always = range(2)

map_color = {
    'none': ColorMode.NoColor,
    'always': ColorMode.Always
}

# Mappings to color codes for particular types of files / file extensions
color_main = collections.defaultdict(lambda: '0')
color_ext = collections.defaultdict(lambda: '0')


## Internal Constants

# The characters to use in tree representation
class Chars:
    # Vertical Line
    Vrt = chr(9474)
    # Tee
    Tee = chr(9500)
    # Horizontal Line
    Hrz = chr(9472)
    # Bottom Corner
    Crn = chr(9492)
    # Newline Character
    Nln = chr(10)

# The strings to concatenate together to form the tree structure
class Segs:
    Vertical = Chars.Vrt + "   "
    Tee = Chars.Tee + Chars.Hrz + Chars.Hrz + " "
    Bottom = Chars.Crn + Chars.Hrz + Chars.Hrz + " "
    Blank = "    "


class Node(object):

    def __init__(self, label=None):

        self.label = label
        self.children = {}
        self.count = 0
        self.info = None


class Tree(object):

    """
    Contains the information on the data that has already been parsed, and
    methods to parse data

    """

    def __init__(self, args):

        self.args = args
        
        self.color = args.color == ColorMode.Always

        self.root = Node()

        self.dir_count = 0
        self.file_count = 0

    def add_line(self, line):

        """
        Parse a line using the correct mode
        """

        line = line.strip()

        path = None
        info = {}

        if self.args.mode == ParsingMode.Normal:
            path = line
            
        elif self.args.mode == ParsingMode.Grep:

            if line.startswith("Binary file ") and line.endswith(" matches"):
                path = line[12:][:-8]
                info['binary'] = True
            else:
                try:
                    (f, match) = line.split(':', 1)
                except ValueError:
                    print("ERROR: Input Text is not known grep output: {}"
                          .format(line))
                    exit()
                else:
                    path = f

        

        if path is not None:
            node = self.root

            for i, seg in enumerate(split_path(path)):

                if seg not in node.children:
                    node.children[seg] = Node(seg)

                node = node.children[seg]
        
            node.info = info
            node.count += 1


    def print_tree(self, node=None, prefix=[], prefix_string='',
                   parent_path=''):

        """
        Print the tree as required (recursively)

        """

        if node is None:
            node = self.root


        # Only true if not the "top level" empty node
        increase_prefix = False
        path = parent_path

        if node.label is not None:
            path = os.path.join(path, node.label)

            sys.stdout.write(prefix_string)

            # Get properties about this file / directory
           
            if len(node.children) > 0 or os.path.isdir(path):
                self.dir_count += 1

                sys.stdout.write(color(node.label, color_main['di'],
                                       self.color))
                    
            else:
                self.file_count += 1

                if self.args.mode == ParsingMode.Grep:
                    # Show count
                    if 'binary' in node.info and node.info['binary']:
                        sys.stdout.write('[{}] '
                                         .format(color('BIN',
                                                       color_main['bin'],
                                                       self.color)))
                    else:
                        sys.stdout.write('[{}] '
                                         .format(color(node.count,
                                                       color_main['count'],
                                                       self.color)))

                (f, ext) = os.path.splitext(path)
                sys.stdout.write(color(node.label, color_ext[ext],
                                       self.color))

            sys.stdout.write(Chars.Nln)

            increase_prefix = True

        if len(node.children) > 0:

            # Default (current) prefix
            child_prefix_mid = prefix
            child_prefix_bot = prefix
            child_prefix_string_mid = ''
            child_prefix_string_bot = ''

            if increase_prefix:
                child_prefix = ''
                for i in prefix:
                    if i:
                        child_prefix += Segs.Vertical
                    else:
                        child_prefix += Segs.Blank

                child_prefix_mid = child_prefix_mid + [1]
                child_prefix_bot = child_prefix_bot + [0]
                child_prefix_string_mid = child_prefix + Segs.Tee
                child_prefix_string_bot = child_prefix + Segs.Bottom

            j = 0
            last = len(node.children) - 1
            for i, child in sorted(node.children.items()):
                if j == last:
                    self.print_tree(child, child_prefix_bot,
                                    child_prefix_string_bot, path)
                else:
                    self.print_tree(child, child_prefix_mid,
                                    child_prefix_string_mid, path)
                j += 1


def split_path(path, l=None):

    """
    Split up a string path into a list of each element
    """

    if l is None:
        l = []
    (head, tail) = os.path.split(path)
    if head and head != path:

        split_path(head, l)
        l.append(tail)
    else:
        l.append(head or tail)
    return l


def setup_color(args):

    """
    Using environment variables, setup the dictionaries of colour lookups
    """

    if args.color == ColorMode.NoColor:
        return

    def parse_environment_variable(var):
        if var in os.environ:
            for entry in os.environ[var].split(':'):
                if entry != '':
                    try:
                        match, color = entry.split('=')
                    except ValueError:
                        print("ERROR: Could not understand entry {} in "
                              "environment variable {}".format(entry, var))
                        exit(1)
                    else:
                        if match.startswith("*."):
                            color_ext[match[1:]] = color
                        else:
                            color_main[match] = color

    color_main['count'] = '01;32'
    color_main['bin'] = '01;35'

    parse_environment_variable('LS_COLORS')

    parse_environment_variable('TREE_COLORS')


def color(string, color, do_color):
    """
    Wrap a string in an ansi color code
    """

    if do_color:
        return '\033[{}m{}\033[0m'.format(color, string)
    else:
        return string

def main():

    """
    Run when the program is being used standalone, uses stdin as the input
    """

    parser = argparse.ArgumentParser(description='Tree is a small utility '
                                     'that displays input from stdin in a '
                                     'tree-like structure')

    parser.add_argument('-i', '--mode', '--input-mode',
                        choices=map_mode,
                        default='none',
                        nargs='?',
                        const='normal',
                        help='The input type. If ommitted, the default type '
                        'is "none", and the directory tree is walked, if -i '
                        'is given with no argument, then "normal" is used'
                    )

    parser.add_argument('-c', '--color', '--colour',
                        choices=map_color,
                        default='always',
                        help='Use color or not, default: "always"'
                    )

    args = parser.parse_args()

    # Convert strings to correct integer
    args.mode = map_mode[args.mode]
    args.color = map_color[args.color]

    # Create Tree
    t = Tree(args)

    # Setup colour dicts using environment variables
    setup_color(args)

    # If the mode is ParsingMode.NoInput, we walk the directory structure
    # instead
    if args.mode == ParsingMode.NoInput:
        print("Walking the directory tree is not currently supported, please "
              "use -i and pipe in input from find")
        exit(1)

    else:
        try:
            for line in sys.stdin:
                t.add_line(line)
        except KeyboardInterrupt:
            # Gracefully handle interrupt when stdin is not being piped and
            # user exits
            pass
        except UnicodeDecodeError:
            print("ERROR: tree.py could not read from stdin!")
            exit(1)


    t.print_tree()

    print ("\n{} director{}, {} file{}".format(t.dir_count,
                                               "y" if t.dir_count == 1 else "ies",
                                               t.file_count,
                                               "s"[t.file_count==1:]))

if __name__ == "__main__":
    main()
