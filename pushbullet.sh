#!/bin/bash

# sends a push notification to my phone
# found here: http://www.pratermade.com/2014/08/use-pushbullet-to-send-notifications-from-your-pi-to-your-phone/

API="o.Fe4bLE0rAjwiM236xbF7VvYrMJm84EsB"
MSG="$1"
DEVICE="ujD2LTz2CHssjAfjsY6kTI"

curl -u $API: https://api.pushbullet.com/v2/pushes -d device_iden="$DEVICE" -d type="note" -d title="News from the iMac!" -d body="$MSG"
