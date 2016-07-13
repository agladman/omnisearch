#!/usr/bin/env python3

# trying to run pdfgrep from within python3

import sys, subprocess
# filepath = ''.join(sys.argv[1:])
filepath = '../../testvol.pdf'
pattern = ' ; '

# argstring = 'pdfgrep -n \'{}\' {}'.format(pattern, filepath)
# output = subprocess.check_output([argstring], shell=True)

output = subprocess.check_output('pdfgrep -n \'{}\' {}'.format(pattern, filepath), shell=True)
print(output)

# success!
