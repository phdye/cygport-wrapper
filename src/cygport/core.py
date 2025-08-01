#!/usr/bin/env python3
#------------------------------------------------------------------------------
#
# Wrapper allowing '.' for CYGPORT_FILE instead of <package-name>-<verison>.cygport
# -- i.e. less typing
#
#------------------------------------------------------------------------------

"""
cygport is a utility for creating and building Cygwin software packages.

Usage: cygport [options] <cygport-file> <command>...

[local enhancements]

If CYGPORT_FILE is '.', it is found in the current directory.  It is
an error if one is not found or more than one are present.  And,
no more than one argument should be '.'.

Command 'build' is replaced with the commands: prep compile test

Option '--log' runs each <command>  as "logts -t -b log/#.<command> cygport ..."

[-----]

OPTIONS may include the following:

  --log, -l    Log via "logts -t -b log/#.<command> cygport ..."
  --32, -4     build package for i686 Cygwin
  --64, -8     build package for x86_64 Cygwin
  --debug      enable debugging messages

The --32 and --64 options are mutually exclusive.

On Cygwin, if neither the --32 nor --64 options are enabled,
the package will be built for the architecture on which cygport
is run.  On other systems, one of those options is required.

COMMAND may be one or more of the following:

  download      download upstream sources from Internet
  prep          create working directory, unpack sources and apply patches
  compile       run all compilation steps
  test          run the package's test suite, if one exists
  build         alias for [ prep compile test ]
  install       install into a DESTDIR, and run post-installation steps
  package       create binary and source packages
  package-test  create binary and source packages, marked as test
  upload        upload finished packages to cygwin.com
  announce      send an announcement email to cygwin.com
  finish        delete the working directory
  all           run prep, compile, install and package

See the included README file for further documentation.

Report bugs to <cygwin-apps@cygwin.com>.
Except about '.' for CYGPORT_FILE.  That is all <philip@phd-solutions.com>.
"""

from __future__ import print_function

import sys
import os
import subprocess
from glob import glob
from copy import copy

from .vendor import docopt

from cygport import __version__

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4).pprint

# from enum import IntEnum
# class order(IntEnum):

CYGPORT_COMMAND = os.environ.get('CYGPORT_COMMAND', '/usr/bin/cygport')

ordinals = {
    'download'      : 0,
    'prep'          : 1,
    'compile'       : 2,
    'test'          : 3,
    'build'         : 4, # prep compile test
    'install'       : 5,
    'package'       : 6,
    'package-test'  : 7,
    'upload'        : 8,
    'announce'      : 9,
    'finish'        : 90,
    'unknown'       : 95,
    'all'           : 99,
}

#------------------------------------------------------------------------------

def main ( argv = sys.argv ) :

    args = docopt.docopt(__doc__, argv=argv[1:], options_first=True, version=__version__ )

    argv[0] = CYGPORT_COMMAND

    # Replace '.' <cygport-file> with only .cygport file in CWD
    if args['<cygport-file>'] == '.':
        cygports = glob('*.cygport')
        if len(cygports) < 1 :
            print(
                "cygport:  No .cyport file found.  For usage 'cygport --help'",
                file=sys.stderr,
            )
            raise SystemExit(1)
        if len(cygports) > 1 :
            print(
                "cygport:  More than one .cyport file found.  For usage 'cygport --help'",
                file=sys.stderr,
            )
            raise SystemExit(1)
        idx = argv.index('.')
        args['<cygport-file>'] = argv[idx] = cygports[0]

    cygport_idx = argv.index(args['<cygport-file>'])
    argx = [ * argv[:cygport_idx+1] ]
    commands = args['<command>']
    # print(f"i : argx  = {argx}")
    # print(f"commands  = {commands}")

    # Expand 'build' into 'prep', 'compile', 'test'
    if 'build' in commands:
        # Insert into COMMAND list
        build = ['prep', 'compile', 'test']
        offset = 0
        for idx, cmd in enumerate(copy(commands)):
            if cmd == 'build':
                idx += offset
                offset += len(build) - 1
                del commands[idx]
                commands[idx:idx] = build

        # print(f"commands  = {commands}")

    # Log each command ?
    logging = args['--log']
    if logging:
        # remove the bespoke logging flag
        idx = argx.index('--log') if '--log' in argx else argx.index('-l')
        del argx[idx]
        # print(f"l : argx  = {argx}")

    n_unknown = ordinals['unknown']
    rc = 0
    for command in commands:
        argz = []
        if logging:
            n = ordinals.get(command, n_unknown)
            argz = [ 'logts', '-t', '-b', f"log/{n}.{command}" ]
        argz += [ *argx, command ]
        if logging:
            print(f"+ {' '.join(argz)}\n")
        proc = subprocess.run(argz)
        rc = proc.returncode
        if logging:
            print()
    return rc

#------------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(main(sys.argv))

#------------------------------------------------------------------------------
