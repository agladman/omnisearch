#!/usr/bin/env python3

"""omnisearch.py automates searches for patterns stored on the file(s)
    passed from OS X service 'Run Proof searches' TODO: amend the
    service to run this and not the .sh version.
    """

import datetime
import logging
# import notify
import os
# import re
import sys
import subprocess

logging.basicConfig(
    filename='logs/omnisearch-{:%Y%m%d-%H%M}.txt'.format(
        datetime.datetime.now()),
        level=logging.DEBUG,
        format=' %(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.CRITICAL)  # comment out this line to enable logging
logging.info('Start of program')

# filepath is passed as sys arg;
# if not script asks for it; absolute path obtained
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
                print('Check file or folder exists and try again.')
        except Exception as e:
            print('Error getting the filepath: {0}'.format(str(e)))
            logging.critical('Exception getting filepath: {0}'.format(str(e)))

cleanpath = os.path.abspath(filepath)

if os.path.isfile(cleanpath):
    searchtype = 'liverun'
elif os.path.isdir(cleanpath):
    searchtype = 'proofrun'
else:
    raise FileNotFoundError('Something went wrong checking the filepath.')
    logging.critical('Exception checking filepath')

logging.debug('searchtype set to {0}'.format(searchtype))

output_path = '{0}/logs'.format(os.path.dirname(cleanpath))
output_dir = os.makedirs(output_path, exist_ok=True)
logging.debug('output_dir: {0}'.format(output_dir))

if searchtype == 'liverun':
    output_file = open('{0}/{1}-{:%Y%m%d-%H%M}.txt'.format(
        output_path,
        os.path.basename(cleanpath).rstrip('.pdf'),
        datetime.datetime.now()), 'a')

    try:
        offset = int(subprocess.check_output('./getFolio.sh', shell=True))
    except Exception as e:
        print('Error fetching the folio: {0}'.format(str(e)))
        logging.critical('Exception fetching folio: {0}'.format(str(e)))

    offset -= 1
    logging.debug('offset is {0}'.format(offset))

elif searchtype == 'proofrun':
    output_file = open('{0}/proofrun-{:%Y%m%d-%H%M}.txt'.format(
        output_path,
        datetime.datetime.now()), 'a')
logging.debug('output destination set to {0}'.format(output_file))

with open('patterns.txt') as f:
    patterns = f.read().split()

search_output = []  # list that will eventually hold results from pdfgrep


def pdfgrepCall(patterns, searchfile):
    fnoutput = []
    for pattern in patterns:
        result = subprocess.check_output(
            'pdfgrep -H -n "{0}" {1}'.format(pattern, searchfile), shell=True)
        for line in result:
            templine = '{0}:\t{1}'.format(pattern, line)
            fnoutput.append(templine)
            return fnoutput

if searchtype == 'proofrun':
    for i in os.listdir(cleanpath):
        searchfile = i
        for line in pdfgrepCall(patterns, searchfile):
            search_output.append(line)

elif searchtype == 'liverun':
    searchfile = cleanpath
    for line in pdfgrepCall(patterns, searchfile):
        search_output.append(line)

    # TODO: in some case, adjust results for folio offset

    # pnum_regex = re.compile(r'^(\d{1,4})\:(.*)$')

    # for line in search_output:
    #     n1 = re.match(pnum_regex, line)
    #     n2 = n + offset
    #     re.sub(n1, n2)

    # TODO: in some case, reformat results

    # pattern = ''
    # pattern_regex = re.compile(r'^§\d{,2}/\d{,2}\:(.*)$')

    # output_data = []

    # for i in search_output:
    #     p = re.match(pattern_regex, i)
    #     n = re.match(pnum_regex, i)
    #     if p:
    #         pattern = p.group(1).strip()
    #         logging.debug('pattern changed to: {}'.format(pattern))
    #     elif n:
    #         # append leading zeros
    #         num = n.group(1)
    #         while len(num) < 4:
    #             num = '0{}'.format(num)

    #         result = '{}:\t{}:\t{}'.format(num, pattern, n.group(2))
    #         # logging.debug('result: {}'.format(result))

    #         output_data.append(result)

# TODO: write results to output_file

# sort into page number order and write to the output file
output_data = search_output  # just while debugging

output_data.sort()
for item in output_data:
    output_file.write(item)

# TODO: print other useful information to output file: date, input file
# or folder name, start time, total runtime

# TODO: notify user on progress through script
# notify function written and imported but not yet implemented in this script
# usage notify.send(title, message, 's', 'p')
