#!/usr/bin/env python3

"""Omnisearch.py automates searches on one or more PDFs against patterns
    loaded from the file patterns.txt, which must be stored in the same
    directory as this script. Other dependencies to be stored in the
    same directory are getFolio.sh and notify.py.
    """

import datetime
import logging
import notify
import os
import re
import sys
import subprocess
import time

start_time = time.time()
search_time = '{:%Y%m%d-%H%M}'.format(datetime.datetime.now())

logging.disable(logging.CRITICAL)  # comment out this line to enable logging
logging.basicConfig(
    filename='logs/omnisearch-{0}.txt'.format(search_time),
    level=logging.DEBUG,  # change to .DEBUG for more detailed logging
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
        self.match_total = 0

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
                'error: {0}\n'
                'script will continue without calculating offset'.format(e))
            logging.error('continuing with default offset')
        finally:
            pass

        if self.offset > 0:
            self.offset -= 1
            logging.info('offset is {0}'.format(self.offset))

    def run_searches(self):
        for i, pattern in enumerate(self.patterns):
            j = i + 1  # to use as num below before it is reassigned as an obj
            i = PatternSearch(pattern, self.filename, self.offset)
            i.call_pdfgrep()
            self.results.append(i)
            k = len(self.patterns)
            title = 'omnisearch: {0}'.format(os.path.basename(self.filename))
            message = '--{0}/{1} complete in {1}s'.format(
                j, k, str(i.duration))
            notify.send(title, message)
        self.count_matches()

    def count_matches(self):
        sum = 0
        for obj in self.results:
            sum += len(obj.match_data)
        self.match_total = sum


class PatternSearch(SearchGroup):
    """Runs searches for a single pattern, stores and formats results,
        records time taken to perform search.
        """

    def __init__(self, pattern, filename, offset):
        self.filename = filename
        self.pattern = pattern.strip('\n')
        self.offset = offset
        self.match_data = []  # results of searches with matches
        self.nonmatch_data = []  # list of searches with zero results
        self.output_data = []  # results with matches formatted for output
        self.start = time.time()
        logging.debug('start time captured: {0}'.format(self.start))
        self.duration = 0.00

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
        # logging.debug('proc_output: {0}'.format(proc_output))
        if not proc_output[0] and not proc_output[1]:  # i.e. both parts of tuple are ''
            x = (self.pattern, 'no matches')
            self.nonmatch_data.append(x)
            # logging.debug('tuple appended to nonmatch_data: {0}'.format(x))
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
                        # logging.debug('tuple appended to match_data: {0}'.format(x))
                    prevline = line
        self.duration = round(time.time() - self.start, 2)
        logging.debug('duration set to {0}s'.format(self.duration))

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
                while len(pnum) < 4:
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

    # capture filepath either as sys arg or from user input
    if len(sys.argv) > 1:
        while True:
            argv = ''.join(sys.argv[1:])
            if os.path.exists(si):
                filepath = argv
                break
    if not filepath:
        while True:
            ui = input('Enter filepath: ')
            if os.path.exists(ui):
                filepath = ui
                break
            else:
                print('Check file or folder exists and try again.')

    # populate search queue
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

    # perform searches
    SearchGroups = []
    for i, file in enumerate(search_queue):
        logging.debug('fetched {0} from search queue at {1}'.format(file, i))
        i = SearchGroup(file, patterns)
        if len(search_queue) == 1:
            i.fetch_offset()
        i.run_searches()
        SearchGroups.append(i)
        logging.debug('searches completed for {0}'.format(file))

    # create summary and output data
    summary_head = '{0}: ran {1} searches on {2} files'.format(
        search_time, len(patterns), len(SearchGroups))
    summary_body = ''
    for obj in SearchGroups:
        nonmatched = []
        body = []
        if obj.match_total == 1:
            match_total_string = '1 result'
        else:
            match_total_string = '{0} results'.format(obj.match_total)
        summary_body += '\n\nsearches on {0}: {1}'.format(
            os.path.basename(obj.filename), match_total_string)
        for res in obj.results:
            a = len(res.match_data)
            b = len(res.nonmatch_data)
            if b:
                nonmatched.append(res.pattern)
                summary_body += '\n\t{0}\t: {1}'.format(
                    res.pattern, '0'.rjust(4, ' '))
            else:
                logging.debug('formatting output for {0}, pattern is: {1}.'.format(
                    obj.filename, res.pattern))
                summary_body += '\n\t{0}\t: {1}'.format(
                    res.pattern, str(a).rjust(4, ' '))
                res.format_output()
            for line in res.output_data:
                body.append(line)
        body.sort()
        if obj.offset > 0:
            adjline = '; page nums match print folios; offset is {0}'.format(
                obj.offset)
        else:
            adjline = ''
        header = '{file}, {time}: {results} results from {searches} searches{adjline}.'.format(
            results=len(body),
            searches=len(patterns),
            file=os.path.basename(obj.filename),
            time=search_time,
            adjline=adjline)
        footer = '\n\nPatterns with zero results: \n'
        for item in nonmatched:
            footer += '\t{0}'.format(item)

        # write output file
        os.chdir(dirb)
        with open(obj.output_file, 'a') as f:
            f.write(header)
            f.write('\n\n---START---\n')
            for line in body:
                f.write(line + '\n')
            f.write('---END---')
            if len(nonmatched) > 0:
                f.write(footer)
            else:
                f.write('\n\nAll searches found matches in the data.')
        os.chdir(dira)

    # produce summary
    os.chdir(dirb)
    run_time = round(time.time() - start_time, 2)
    runtime_string = '\n\nrunning time: {0}s'.format(run_time)
    summary = summary_head + summary_body + runtime_string
    summary_file = 'summary-{0}.txt'.format(search_time)
    with open(summary_file, 'a') as s:
        s.write(summary)
    os.chdir(dira)
    print(summary)

    # finish off and notify
    print('Script complete.')
    notify.send('omnisearch: script complete',
                'running time {0}s'.format(run_time), 's', 'p')
    logging.info('end of program; running time: {0}s'.format(run_time))
