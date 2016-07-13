#!/usr/bin/env python3

# omnisearch.py automates searches for patterns stored TODO: <where?> on the file(s) passed from
# OS X service 'Run Proof searches' TODO: amend the service to run this and not the .sh version.

import sys, os, re, logging, datetime, notify, subprocess

logging.basicConfig(filename='logs/omnisearch-{:%Y%m%d-%H%M}.txt'.format(datetime.datetime.now()), level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.CRITICAL) # comment out this line to enable logging
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
    raise FileNotFoundError('Something went wrong checking the filepath.')
    logging.critical('Exception checking filepath')

logging.debug('searchtype set to {}'.format(searchtype))

# TODO: create output file
# create logs folder and output file
output_path = '{}/logs'.format(os.path.dirname(cleanpath))
output_dir = os.makedirs(output_path, exist_ok=True)
logging.debug('output_dir: {}'.format(output_dir))

if searchtype == 'liverun':
    output_file = open('{}/{}-{:%Y%m%d-%H%M}.txt'.format(output_path, os.path.basename(cleanpath).rstrip('.pdf'), datetime.datetime.now()), 'a')

    # capture starting folio for offset calculation
    try:
        offset = int(subprocess.check_output('./getFolio.sh', shell=True))
    except Exception as e:
         print('Something went wrong fetching the folio: {}'.format(str(e)))
         logging.critical('Exception fetching folio: {}'.format(str(e)))

    offset -= 1
    logging.debug('offset is {}'.format(offset))

elif searchtype == 'proofrun':
    output_file = open('{}/proofrun-{:%Y%m%d-%H%M}.txt'.format(output_path, datetime.datetime.now()), 'a')
logging.debug('output destination set to {}'.format(output_file))

# TODO: store search patterns to memory

try:
    with open('patterns.txt') as f:
        patterns = f.readlines()
except Exception as e:
    print('Something went wrong fetching the search patterns: {}'.format(str(e)))
    logging.critical('Exception fetching search patterns: {}'.format(str(e)))

# TODO: run pdfgrep searches and capture results

search_output = [] # list that will eventually hold all the results from pdfgrep

def pdfgrepCall(patterns, searchfile):
    fnoutput = []
    for pattern in patterns:
        result = subprocess.check_output('pdfgrep -H -n "{}" {}'.format(pattern.rstrip('\n'), searchfile), shell=True)
        for line in result:
            fnoutput.append(line)
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

    pnum_regex = re.compile(r'^(\d{1,4})\:(.*)$')

    for line in search_output:
        n1 = re.match(pnum_regex, line)
        n2 = n + offset
        re.sub(n1, n2)

    # TODO: in some case, reformat results

    # pattern = ''
    # pattern_regex = re.compile(r'^§\d{,2}/\d{,2}\:(.*)$')

    output_data = []

    for i in search_output:
        p = re.match(pattern_regex, i)
        n = re.match(pnum_regex, i)
        if p:
            pattern = p.group(1).strip()
            logging.debug('pattern changed to: {}'.format(pattern))
        elif n:
            # append leading zeros
            num = n.group(1)
            while len(num) < 4:
                num = '0{}'.format(num)

            result = '{}:\t{}:\t{}'.format(num, pattern, n.group(2))
            # logging.debug('result: {}'.format(result))

            output_data.append(result)

# TODO: write results to output_file

# sort into page number order and write to the output file
output_data.sort()
for item in output_data:
    output_file.write('{}\n'.format(item))

# TODO: print other useful information to output file: date, input file or folder name, start time, total runtime

# TODO: notify user on progress through script
# notify function written and imported but not yet implemented in this script
# usage notify.send(title, message, 's', 'p')
