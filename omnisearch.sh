#!/bin/bash

# Runs searches for patterns stored in the array on the file(s) passed from
# OS X service 'Run Proof searches' as $1.

# Script created 20/06/2016, last updated 23/06/2016

# capture start time for runtime calculation
res1=$(date +"%s")

# notify function puts output in useful places
# notify "message" -s (sticky) -p (also send to pushbullet)
notify() {
	echo "$1"
	growlnotify "$2" -a terminal -t "OmniSearch" -m "${1}"
	if [ "$3" ]
		then ./pushbullet.sh "$1"
	fi
}

# store search patterns in an array
declare -a patterns='(
	[0]=" ; " # §1-Punctuation, blank tags
	[1]=" , "
	[2]=" \. "
	[3]=":;"
	[4]=":,"
	[5]=":\."
	[6]="\.\."
	[7]="\-\-"
	[8]="_-"
	[9]=" - "
	[10]="w{4}\." # §2-Contact fields
	[11]="http"
	[12]="@@"
	[13]=" (F|f)ax "
	[14]="(S|s)tr " # §3-Abbreviations
	[15]=" (U|u)niv "
	[16]=" Acad "
	[17]=" (A|a)vda\."
	[18]=" (A|a)ve\."
	[19]=" (R|r)d\."
	[20]=" (S|s)t\."
	[21]=" (frm|frmly) "
	[22]="etc(;|,)"
	[23]=" (A|a)dmin " # §4-Job titles
	[24]="; Chair "
	[25]="Assoc "
	[26]="Dir\.? Gen\.?"
	[27]="Gen\.?-Sec\.?"
	[28]="Pres "
	[29]="Vice Dean"
	[30]="(Man-Dir|Man-Dir\.)"
	[31]="(Sec-Gen|Sec\.-Gen!\.|Sec-Gen\.)"
	[32]="Dir\."
	[33]="Pro Vice-Chancellor"
	[34]="audio-visual" # §5-Library holdings and publications
	[35]="(E|e)-(book|Book|journal|Journal)"
	[36]="(D|d)ocs? "
	[37]="( videos | tapes )"
	[38]="(A|a)nnual (R|r)eport"
	[39]="(Y|y)earbook"
	[40]="DELETE" # §6-Miscellaneous
	[41]="[^Sec]\.-[^A-Za-z]"
	[42]="[A-Za-z0-9]+Campus"
	[43]="[0-9][A-Za-z]+ Campus:"
	[44]="[0-9] [A-Za-z]+ Campus:"
	[45]=":see"
	[46]=":email"
)'

# check the file or directory passed as $1 exists and if not exit with an error message plus sticky growl notification
test -e "$1" || { notify "File not found" -s ; exit 1 ; }

# test whether $1 is a file or a directory and set search type
if [ -d "$1" ]
	then searchtype="proofrun" && filecount=$(ls "$1" | wc -l)

	# create the logs
	mkdir -p "$1"/logs
	log="$1"/logs/$(date +"%Y%m%d-%H%M")-"$searchtype".txt

	# label log with number of files, directory  and date
	printf "Searches run on %s files in %s, %s" "$filecount" "$1" "$(date +"%d-%m-%Y")" >> "$log" 2>&1

elif [ -f "$1" ]
	then searchtype="liverun"

	# code to capture $folio adapted from http://stackoverflow.com/a/9186520/6409460
	folio="$(osascript -e 'Tell application "System Events" to display dialog "Enter the starting folio:" default answer ""' -e 'text returned of result' 2>/dev/null)"
		if [ "$?" -ne 0 ]; then
		    # The user pressed Cancel
		    exit 1 # exit with an error status
		elif [ -z "$folio" ]; then
		    # The user left the folio blank
		    osascript -e 'Tell application "System Events" to display alert "You must enter a folio; cancelling..." as warning'
		    exit 1 # exit with an error status
		fi

	# create the logs
	mkdir -p "$(dirname "$1")/logs"
	log=$(dirname "$1")/logs/$(date +"%Y%m%d-%H%M")-"$searchtype".txt
	flog=$(dirname "$1")/logs/$(date +"%Y%m%d-%H%M")-"$searchtype"-folios.txt

	# label log with proof filename and date
	printf "Searches run on %s, %s" "$(basename "$1")" "$(date +"%d-%m-%Y")" >> "$log" 2>&1

else
	{ notify "Filetype error" -s ; exit 2 ; }

fi

# variables
count=0 # to count how many times we've iterated through the search loops below
total=${#patterns[@]} # how many searches there are to run through

# print start time to logs
printf "\n\nSearches began at %s" "$(date +"%T")" >> "$log" 2>&1

# run the searches
if [[ $searchtype == "proofrun" ]]
then
	for pattern in "${patterns[@]}"; do
		(( ++count ))
		printf "\n\n§%s/%s: '%s'\n" "$count" "$total" "$pattern" >> "$log" 2>&1
		pdfgrep -H -n "$pattern" "$1"/*.pdf >> "$log" 2>&1 # search all files in the directory
		notify "--$count/$total"
	done

elif [[ $searchtype == "liverun" ]]
then
	for pattern in "${patterns[@]}"; do
		(( ++count ))
		printf "\n\n§%s/%s: '%s'\n" "$count" "$total" "$pattern" >> "$log" 2>&1
		pdfgrep -n "$pattern" "$1" >> "$log" 2>&1 # search just that one file
		notify "--$count/$total"
	done

else
	{ notify "There was a problem with the search conditional" -s ; exit 3 ; }
fi

# capture end time and calculate runtime
res2=$(date +"%s")
dt=$(echo "$res2 - $res1" | bc)
dd=$(echo "$dt/86400" | bc)
dt2=$(echo "$dt-86400*$dd" | bc)
dh=$(echo "$dt2/3600" | bc)
dt3=$(echo "$dt2-3600*$dh" | bc)
dm=$(echo "$dt3/60" | bc)
ds=$(echo "$dt3-60*$dm" | bc)

printf "\n\nTotal runtime: %d:%02d:%02d:%02.4f\n" "$dd" "$dh" "$dm" "$ds" >> "$log" 2>&1

# adjust for folio offset but only for liverun searches
if [[ $searchtype == "liverun" ]]
then
	notify "Adjusting for folio offset"

	# calculate the offset
	(( --folio ))

	# perl from here http://stackoverflow.com/a/37571771/6409460
	perl -pe "s/^(\d{2,4}):/\$1 + $folio . ':'/e" "$log" &> "$flog" 2>&1

notify "Formatting log"
python3 cleanlog.py $flog

fi

# exit
notify "Script ended successfully" -s -p
