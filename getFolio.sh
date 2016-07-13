#!/bin/bash

folio="$(osascript -e 'Tell application "System Events" to display dialog "Enter the starting folio:" default answer ""' -e 'text returned of result' 2>/dev/null)"
if [ "$?" -ne 0 ]; then
    # The user pressed Cancel
    exit 1 # exit with an error status
elif [ -z "$folio" ]; then
    # The user left the folio blank
    osascript -e 'Tell application "System Events" to display alert "You must enter a folio; cancelling..." as warning'
    exit 1 # exit with an error status
fi
echo $folio
