#!/usr/bin/env python3

# trying to run pdfgrep from within python3

import sys, subprocess
# filepath = ''.join(sys.argv[1:])
filepath = '/Users/anthonygladman/Documents/Liverun/vol1.pdf'
pattern = ' ; '
argstring = 'pdfgrep -n \'{}\' {}'.format(pattern, filepath)
output = subprocess.run([argstring], shell=True)
print(output)

# success!
