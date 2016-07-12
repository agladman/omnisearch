#!/usr/bin/env python3

# omnisearch.py automates searches for patterns stored TODO: <where?> on the file(s) passed from
# OS X service 'Run Proof searches' TODO: amend the service to run this and not the .sh version.

import sys, os, re, logging, datetime, notify

logging.basicConfig(filename='logs/omnisearch-{:%Y%m%d-%H%M}.txt'.format(datetime.datetime.now()), level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
# logging.disable(logging.CRITICAL) # comment out this line to enable logging
logging.info('Start of program')

# TODO: capture input filepath
# TODO: check that input filepath exists

# filepath is passed as sys arg; if not script asks for it; absolute path obtained
if len(sys.argv) > 1:
    filepath = ''.join(sys.argv[1:])
else:
    while True:
        try:
            ui = input('Enter filepath: ')
            if os.path.exists(ui):
                filepath = ui
                break
            else:
                print('Check file or folder exists in that location and try again.')
        except Exception as e:
            print('Something went wrong getting the filepath: {}'.format(str(e)))
            logging.critical('Exception getting filepath: {}'.format(str(e)))

cleanpath = os.path.abspath(filepath)

# TODO: check whether input is a file or a directory and stores this in a variable

if os.path.isfile(cleanpath):
    searchtype = 'liverun'
elif os.path.isdir(cleanpath):
    searchtype = 'proofrun'
else:
    raise FileNotFoundError as e:
        print('Something went wrong checking the filepath: {}'.format(str(e)))
        logging.critical('Exception checking filepath: {}'.format(str(e)))

logging.debug('searchtype set to {}'.format(searchtype))

# TODO: create output file
# create logs folder and output file
output_dir = os.path.mkdir('{}/logs'.format(os.path.dirname(cleanpath), exist_ok))
if searchtype == 'liverun':
    output_file = open('{}/{}-{:%Y%m%d-%H%M}.txt'.format(output_dir, os.path.basename(cleanpath).strip('.txt'), datetime.datetime.now()))
    # TODO: capture starting folio for offset calculation
elif searchtype == 'proofrun':
    output_file = open('{}/proofrun-{:%Y%m%d-%H%M}.txt'.format(output_dir, datetime.datetime.now()))
logging.debug('output destination set to {}'.format(output_file))

# TODO: store search patterns to memory

try:
    with open('patterns.txt') as f:
        patterns = f.readlines()
except Exception as e:
    print('Something went wrong fetching the search patterns: {}'.format(str(e)))
    logging.critical('Exception fetching search patterns: {}'.format(str(e)))

# TODO: run pdfgrep searches and capture results

# TODO: in some case, adjust results for folio offset

# TODO: in some case, reformat results

# TODO: write results to output_file

# TODO: print other useful information to output file: date, input file or folder name, start time, total runtime

# TODO: notify user on progress through script
# notify function written and imported but not yet implemented in this script
# usage notify.send(title, message, 's', 'p')
