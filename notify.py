#!/usr/bin/env python3
import subprocess

def send(title, message, sticky='', push=None):
    # make sure to import subprocess

    # sends notification to growl, or sticky notification if flag present
    sticky = '-s ' if sticky else sticky
    subprocess.run('growlnotify {}-a terminal -t "{}" -m "{}"'.format(sticky, title, message), shell=True)

    # also sends same notification to pushbullet if flag present
    if push:
        # reads api key and device id from external file into pbdict
        pbdict = {}
        try:
            with open('../../pbdict.txt', 'r') as f:
                for line in f:
                    splitLine = line.split()
                    pbdict[splitLine[0]] = ','.join(splitLine[1:])
        except Exception as e:
            return e

        subprocess.run('curl -u {}: https://api.pushbullet.com/v2/pushes -d device_iden="{}" -d type="note" -d title="{}" -d body="{}"'.format(pbdict['api'], pbdict['device'], title, message), shell=True)

if __name__ == '__main__':

    print('Preparing to send a test notification...')
    try:
        title = input('Enter the notification title: ')
        message = input('Enter the notification body: ')
    except Exception as e:
        raise
    send(title, message, 's', 'p')
