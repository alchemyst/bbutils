#!/usr/bin/env python
from __future__ import print_function

import os
import sys
import argparse

parser = argparse.ArgumentParser('Split files from ClickUP')
parser.add_argument('--pretend', default=False, action='store_true',
                    help='Only pretend to do the naming')
parser.add_argument('--skip', default='',
                    help='levels to skip (0 indexed) eg 0,3 will skip the first and fourth levels')
parser.add_argument('--delimiter', default='_',
                    help='delimiter to use to split fields')
parser.add_argument('--studentfield', default=0, type=int,
                    help='Field to use for studentnumber - only makes sense if renaming from file with --classlist')
# FIXME: encodings work correctly for Python3
parser.add_argument('--classlist', type=argparse.FileType('r', encoding='utf-8-sig'),
                    help='Grade Center file to read from (csv)')
parser.add_argument('--encoding', default='utf-8-sig',
                    help='Encoding to use for the class list')
parser.add_argument('--format', default='{Last Name}, {First Name}',
                    help='Format for replacing user name')
parser.add_argument('--levels', default=4, type=int, 
                    help='Number of levels')
parser.add_argument('targetdir',
                    help='Directory to run on')

def mkdir(args, d):
    if args.pretend:
        print("making dir", d)
    else:
        os.mkdir(d)
        
def rename(args, a, b):
    if args.pretend:
        print("Rename", a, "to", b)
    else:
        os.rename(a, b)
        
def mkdirs(args, dirpart):
    dirname = ''
    for part in dirpart:
        dirname = os.path.join(dirname, part)
        if not os.path.exists(dirname):
            mkdir(args, dirname)
    return dirname

if __name__ == "__main__":
    args = parser.parse_args()

    if args.classlist:
        from csv import DictReader
        # FIXME: Replace this with the io module
        student_reader = DictReader(args.classlist)
        try:
            students = {s['Username']: args.format.format(**s) for s in student_reader}
        except KeyError:
            print("Something's wrong with the keys", student_reader.fieldnames)
            sys.exit(1)

    files = os.listdir(args.targetdir)
    skipcols = [int(n) for n in args.skip.split(',') if n.isdigit()]
    
    for oldname in files:
        s = oldname.split(args.delimiter)
        if len(s) < args.levels:
            print("Invalid file:", oldname)
            continue
        elif len(s) == args.levels: # base level file
            filename = "comments.txt"
            dirpart = s[:args.levels-1] + [os.path.splitext(s[args.levels-1])[0]]
        else:
            dirpart = s[:args.levels]
            filename = "_".join(s[args.levels:])

        dirpart = [part for (i, part) in enumerate(dirpart) if i not in skipcols]

        if args.classlist:
            dirpart[args.studentfield] = students[dirpart[args.studentfield]]
        
        dirname = mkdirs(args, [args.targetdir] + dirpart)
        newname = os.path.join(dirname, filename)
        rename(args, os.path.join(args.targetdir, oldname), newname)
    
