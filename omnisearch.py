#!/usr/bin/env python3

"""omnisearch.py automates searches for patterns stored on the file(s)
    passed from OS X service 'Run Proof searches' TODO: amend the
    service to run this and not the .sh version.
    """

import datetime
import logging
# import notify
import os
import re
import sys
import subprocess

search_time = '{:%Y%m%d-%H%M}'.format(datetime.datetime.now())

# logging.disable(logging.CRITICAL)  # comment out this line to enable logging
logging.basicConfig(
    filename='logs/omnisearch-{0}.txt'.format(search_time),
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
        self.output_path = ''
        self.output_dir = ''
        self.output_file = ''
        self.parse_output()
        self.results = []  # will hold dependent PatternSearch objects
        self.offset = 0

    def parse_output(self):
        dirb = os.path.dirname(self.filename)
        os.chdir(dirb)  # into base dir for output path
        # logging.debug('- cwd changed from {0} to {1}'.format(dira, dirb))
        self.output_path = 'logs'
        try:
            self.output_dir = os.makedirs(self.output_path, exist_ok=True)
            if self.output_dir:
                logging.debug('output_dir created')
            else:
                logging.debug('output_dir already exists')
        except Exception as e:
            logging.critical('exception creating output_dir: {0}'.format(e))
        self.output_file = '{0}/{1}-{2}.txt'.format(
            self.output_path,
            os.path.basename(self.filename).rstrip('.pdf'),
            search_time)
        os.chdir(dira)  # back to script home directory
        logging.info('output destination set to {0}'.format(self.output_file))

    def fetch_offset(self):
        try:
            self.offset = int(subprocess.check_output(
                './getFolio.sh', shell=True))
        except Exception as e:
            logging.warning(
                'error: {0}\nscript will continue without calculating offset'.format(e))
            logging.error('continuing with default offset')
        finally:
            pass

        if self.offset > 0:
            self.offset -= 1
            logging.info('offset is {0}'.format(self.offset))

    def run_searches(self):
        for i, pattern in enumerate(self.patterns):
            i = PatternSearch(pattern, self.filename, self.offset)
            i.call_pdfgrep()
            self.results.append(i)


class PatternSearch(SearchGroup):
    """Runs searches for a single pattern, stores and formats results.
        """

    def __init__(self, pattern, filename, offset):
        self.filename = filename
        self.pattern = pattern.strip('\n')
        self.offset = offset
        self.match_data = []  # results of searches with matches
        self.nonmatch_data = []  # list of searches with zero results
        self.output_data = []  # results with matches formatted for output

    def call_pdfgrep(self):
        cmd = 'pdfgrep -n "{0}" {1}'.format(
            self.pattern,
            self.filename)
        logging.debug('command passed: {0}'.format(cmd))
        proc = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                shell=True,
                                universal_newlines=True)
        proc_output = proc.communicate()  # type is tuple
        logging.debug('proc_output: {0}'.format(proc_output))
        if not proc_output[0] and not proc_output[1]:  # i.e. both parts of tuple are ''
            x = (self.pattern, 'no matches')
            self.nonmatch_data.append(x)
            logging.debug('tuple appended to nonmatch_data: {0}'.format(x))
        else:
            text = proc_output[0].split('\n') + proc_output[1].split('\n')
            prevline = ''
            for line in text:
                if line:
                    # logging.debug('line passed from text: {0}'.format(line))
                    if line == prevline:
                        pass
                    else:
                        x = (self.pattern, line)
                        self.match_data.append(x)
                        logging.debug(
                            'tuple appended to match_data: {0}'.format(x))
                    prevline = line

    def format_output(self):
        # items are tuples, pattern and line
        for i, item in enumerate(self.match_data):
            pattern, line = item
            pnum_regex = re.compile(r'^(\d{1,4})\:(.*)$')
            m = re.search(pnum_regex, line)
            if m:
                pnum = m.group(1)
                rest = m.group(2)
                # calc offset if needed
                if self.offset > 0:
                    x = int(pnum) + self.offset
                    pnum = str(x)
                # add leading zeros
                while len(pnum) > 4:
                    pnum = '0{0}'.format(pnum)
                # swap order and add pattern
                output_line = '{0}: {1}: {2}'.format(
                    pnum, pattern.lstrip(), rest)
                # append to ouput_data
                self.output_data.append(output_line)
                logging.debug('output line {0}: {1}'.format(i, output_line))
            else:
                logging.debug('output line {0} blank so skipped'.format(i))
        self.output_data.sort()

if __name__ == '__main__':

    dira = os.getcwd()

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

    search_queue = []
    cleanpath = os.path.abspath(filepath)
    if os.path.isfile(cleanpath):
        dirb = os.path.dirname(cleanpath)
        search_queue.append(cleanpath)
        logging.debug('added {0} to search queue'.format(cleanpath))
    elif os.path.isdir(cleanpath):
        dirb = cleanpath
        os.chdir(dirb)  # into dir where items are stored
        dir_contents = os.listdir(cleanpath)
        for item in dir_contents:
            if item.startswith('.'):  # exclude .DS_Store etc. from searches
                pass
            elif os.path.isdir(item):  # exclude logs or other subfolders
                pass
            elif os.path.isfile(item):
                item = os.path.abspath(item)
                search_queue.append(item)
                logging.debug('added {0} to search queue'.format(item))
            else:  # some other unforseen circumstance
                pass
        os.chdir(dira)  # back to script home directory

    SearchGroups = []
    for i, file in enumerate(search_queue):
        logging.debug('fetched {0} from search_queue at {1}'.format(file, i))
        i = SearchGroup(file, patterns)
        if len(search_queue) == 1:
            i.fetch_offset()
        i.run_searches()
        SearchGroups.append(i)
        logging.debug('searches completed for {0}'.format(file))

    print('ran {0} searches on {1} files'.format(
        len(patterns), len(SearchGroups)))
    for obj in SearchGroups:
        nonmatched = []
        body = []
        print('searches on {0}: '.format(obj.filename))
        for res in obj.results:
            a = len(res.match_data)
            b = len(res.nonmatch_data)
            if b:
                nonmatched.append(res.pattern)
            else:
                logging.debug('formatting output for {0}, pattern is: {1}.'.format(
                    obj.filename, res.pattern))
                print('\t{0}\t: {1} results'.format(res.pattern, a))
                res.format_output()
            for line in res.output_data:
                body.append(line)

        header = '{file}, {time}: {results} results from {searches} searches.\n\n'.format(
            results=len(body),
            searches=len(patterns),
            file=os.path.basename(obj.filename),
            time=search_time)
        footer = '\nPatterns with zero results: \n'
        for item in nonmatched:
            footer += '\t{0}'.format(item)

        os.chdir(dirb)
        with open(obj.output_file, 'a') as f:
            f.write(header)
            for line in body:
                f.write(line + '\n')
            if len(nonmatched) > 0:
                f.write(footer)
            else:
                f.write('\nAll searches found matches in the data.')
            f.write('\n---END---')
        os.chdir(dira)

    print('Script complete.')
    logging.info('end of program')

    # TODO: print other useful information to output file: date, input file
    # or folder name, start time, total runtime

    # TODO: notify user on progress through script
    # notify function written and imported but not yet implemented in this script
    # usage notify.send(title, message, 's', 'p')
