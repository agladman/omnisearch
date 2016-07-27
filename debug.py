#!/usr/bin/env Python3

with open('patterns.txt', 'r') as f:
    patterns1 = f.readlines()

print('readlines(), pattern')
for i, pattern in enumerate(patterns1):
    print('{0}. \'{1}\''.format(i, pattern))

print('readlines(), pattern.strip(\'\\n\')')
for i, pattern in enumerate(patterns1):
    print('{0}. \'{1}\''.format(i, pattern.strip('\n')))

with open('patterns.txt', 'r') as f:
    patterns2 = f.read().split()

print('read().split(), pattern')
for i, pattern in enumerate(patterns2):
    print('{0}. \'{1}\''.format(i, pattern))

print('read().split(), pattern.strip(\'\\n\')')
for i, pattern in enumerate(patterns2):
    print('{0}. \'{1}\''.format(i, pattern.strip('\n')))