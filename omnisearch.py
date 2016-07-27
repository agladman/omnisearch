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

# logging.disable(logging.CRITICAL)  # comment out this line to enable logging
logging.basicConfig(
    filename='logs/omnisearch-{:%Y%m%d-%H%M}.txt'.format(
        datetime.datetime.now()),
    level=logging.DEBUG,
    format=' %(asctime)s - %(levelname)s - %(message)s')
logging.info('start of program')


class SearchGroup(object):
    """Holds information about the searches run on a file as well as the
        results for each pattern searched in PatternSearch subclass
        objects.
        """
    def __init__(self, filename, patterns):
        self.filename = filename
        self.patterns = patterns
        self.output_path = '{0}/logs'.format(os.path.dirname(self.filename))
        self.output_dir = os.makedirs(self.output_path, exist_ok=True)
        self.output_file = ''
        self.setOutputFile()
        self.results = []  # will hold dependent PatternSearch objects
        self.offset = 0

    def setOutputFile(self):
        self.output_file = '{}/{}-{:%Y%m%d-%H%M}.txt'.format(
            self.output_path,
            os.path.basename(self.filename).rstrip('.pdf'),
            datetime.datetime.now())
        logging.debug('output destination set to {0}'.format(self.output_file))

    def fetchOffset(self):
        try:
            self.offset = int(subprocess.check_output('./getFolio.sh', shell=True))
        except Exception as e:
            print('Error fetching the folio: {0}'.format(str(e)))
            logging.critical('exception fetching folio: {0}'.format(str(e)))

        self.offset -= 1
        logging.debug('offset is {0}'.format(self.offset))

    def runSearches(self):
        for i, pattern in enumerate(self.patterns):
            i = PatternSearch(pattern, self.filename)
            i.pdfgrepCall()
            self.results.append(i)


class PatternSearch(SearchGroup):
    """Holds results of a search run against a given pattern on the
        search file held in its parent SearchGroup object.
        """
    def __init__(self, pattern, filename):
        self.filename = filename
        self.pattern = pattern
        self.output_data = []  # will hold strings of formatted search results
        
    def pdfgrepCall(self):
        cmd = 'pdfgrep -n "{0}" {1}'.format(
            self.pattern.strip('\n'), 
            self.filename)
        logging.debug('command passed: {0}'.format(cmd))
        proc = subprocess.Popen(cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            shell=True, 
            universal_newlines=True)
        text = proc.communicate()  # add [0]?

        prevline = ''
        for line in text:
            logging.debug('line passed from text: {0}'.format(line))
            if line == prevline:
                pass
            else:
                x = (self.pattern, line)
                self.output_data.append(x)
                logging.debug('tuple appended to output_data: {0}'.format(x))
            prevline = line


if __name__ == '__main__':

    with open('patterns.txt') as f:
        patterns = f.readlines()
    
    if len(sys.argv) > 1:
        filepath = ''.join(sys.argv[1:])
    else:
        while True:
            ui = input('Enter filepath: ')
            if os.path.exists(ui):
                filepath = ui
                break
            else:
                print('Check file or folder exists and try again.')

    dir_files = []
    cleanpath = os.path.abspath(filepath)
    if os.path.isfile(cleanpath):
        dir_files.append(cleanpath)
    elif os.path.isdir(cleanpath):
        dir_contents = os.listdir(cleanpath)
        for item in dir_contents:
            if item.startswith('.'):
                pass
            else:
                dir_files.append(item)

    SearchGroups = []
    for i, file in enumerate(dir_files):
        i = SearchGroup(file, patterns)
        if len(dir_files) == 1:
            i.fetchOffset()
        i.runSearches()
        SearchGroups.append(i)

    for obj in SearchGroups:
        a = len(obj.results)
        b = obj.filename
        print('{0} results from {1}'.format(a, b))

    # logging.debug('searchtype set to {0}'.format(searchtype))

    # output_path = '{0}/logs'.format(os.path.dirname(cleanpath))
    # output_dir = os.makedirs(output_path, exist_ok=True)
    # if output_dir:
    #     logging.debug('output_dir created: {0}'.format(output_dir))
    # else:
    #     logging.debug('output_dir already exists')

    # if searchtype == 'liverun':
    #     output_file = '{}/{}-{:%Y%m%d-%H%M}.txt'.format(
    #         output_path,
    #         os.path.basename(cleanpath).rstrip('.pdf'),
    #         datetime.datetime.now())

    #     try:
    #         offset = int(subprocess.check_output('./getFolio.sh', shell=True))
    #     except Exception as e:
    #         print('Error fetching the folio: {0}'.format(str(e)))
    #         logging.critical('exception fetching folio: {0}'.format(str(e)))

    #     offset -= 1
    #     logging.debug('offset is {0}'.format(offset))

    # elif searchtype == 'proofrun':
    #     output_file = '{}/proofrun-{:%Y%m%d-%H%M}.txt'.format(
    #         output_path,
    #         datetime.datetime.now())
    # logging.debug('output destination set to {0}'.format(output_file))

    # with open('patterns.txt') as f:
    #     patterns = f.readlines()

    # search_output = []  # list that will eventually hold results from pdfgrep


    # def pdfgrepCall(patterns, searchfile):
    #     fnoutput = []
    #     for pattern in patterns:
    #         cmd = 'pdfgrep -n "{0}" {1}'.format(pattern.strip('\n'), searchfile)
    #         logging.debug('command passed: {0}'.format(cmd))
    #         proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=False)
    #         text = proc.communicate()

    #         prevline = ''
    #         for line in text:
    #             logging.debug('line passed from text: {0}'.format(line))
    #             if line == prevline:
    #                 pass
    #             else:
    #                 x = (pattern, line)
    #                 fnoutput.append(x)
    #                 logging.debug('tuple appended to fnoutput: {0}'.format(x))
    #             prevline = line

    #     return fnoutput

    # if searchtype == 'proofrun':
    #     for i in os.listdir(cleanpath):
    #         searchfile = i
    #         for fnoutput_tuple in pdfgrepCall(patterns, searchfile):
    #             pattern, line = fnoutput_tuple
    #             newline = '{0}:\t{1}'.format(pattern, line)
    #             search_output.append(newline)

    # elif searchtype == 'liverun':
    #     searchfile = cleanpath
    #     for fnoutput_tuple in pdfgrepCall(patterns, searchfile):
    #         pattern, line = fnoutput_tuple
    #         newline = '{0}:\t{1}'.format(pattern, line)
    #         # logging.debug('tuple unpacked to newline: {0}'.format(newline))
    #         search_output.append(newline)

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
    # output_data = search_output  # just while debugging

    # output_data.sort()
    # with open(output_file, 'a') as f:
    #     for item in output_data:
    #         f.write(item)

    print('Script complete.')
    logging.info('end of program')

    # TODO: print other useful information to output file: date, input file
    # or folder name, start time, total runtime

    # TODO: notify user on progress through script
    # notify function written and imported but not yet implemented in this script
    # usage notify.send(title, message, 's', 'p')
