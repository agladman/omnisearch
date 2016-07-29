# Omnisearch.py
This script automates pdfgrep searches on one or more PDFs and formats the results in log files. It also produces a summary of the results so users can quickly tell whether there are any results, and if so how many there are for each search pattern.
The search patterns are loaded from a text file stored in the same directory.
## Dependencies
### getFolio.sh
Displays a user dialog that asks for the starting folio of the PDF to be searched. This is then used in calculating the folio offset where needed.
### notify.py
This script pushes messages to growl notifcations and, if needed, to pushbullet as well. It loads sensitive information such as API tokens from a text file stored in the user's home directory.