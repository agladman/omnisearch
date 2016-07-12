# The Real Omnisearch, Python Style

- Use requests to send notes via pushbullet: http://docs.python-requests.org/en/latest/index.html
- Use GNTP to send grown notifications: https://github.com/kfdm/gntp/
- build array of patterns from patterns.txt (maybe take out comments from that file first)
- incorporate omnisearch.sh and cleanlog.py into one script
- call pdfgrep from within that script as per test.py
- ask for folio via applescript in similar manner
- run script from automator as python rather than calling python from bash - pass input as stdin
make sure env, path etc. calls python3 not built in 2.7

Aw yeah, this is gonna be awesome baby.

## outline of omnisearch.sh script processes

1. capture input filepath
1. store search patterns to memory
1. check that input filepath exists
1. check whether input is a file or a directory and stores this in a variable
1. create output file
1. run pdfgrep searches and sends results to an output file
1. in some case, adjusts for folio offset
1. in some case, reformats output file
1. print other useful information to output file: date, filename, start time, total runtime
1. notify user on progress through script
