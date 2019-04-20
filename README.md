# Coauthor Network Tracker

The Coauthor Network Tracker is an app to obtain and visualize coauthor networks of any given academic researcher without the usage of any database. This app is internet based, particularly, it uses google search to get find the CV of a researcher in one's personal website or university website no matter it is in pdf format or html. Moreover, the app can also find pdf CV even if it is included as a dropbox or google doc file. After the app obtain a valid CV, it uses natural language processing (NLP) to extract the year of graduation of the research's PhD degree as well as the coauthors. Then the app creates an interactive map to visualize the network. Due to NLP accuracy limit, the results can include non-human names. Thus, the app allows the user to delete those "names" by double-clicking on the names. If the user want, one can store the network data of each researcher and related information in a text file. Finally, In the Analysis Mode, the app can find and highlight a shortest path (if any) between any two nodes in the network.

## Requirements
This app requires python 2 to run.
In addition, the user needs to install the following modules:

  1. Beautiful Soup:
  install: pip install bs4

  2. google search
  install: https://breakingcode.wordpress.com/2010/06/29/google-search-python/
  or use the file "google-1.06.tar.gz" included in the folder

  3. pdfminer
  install: pip install pdfminer

  4. unidecode
  install: pip install unidecode

  5. natural language toolkit
  install: pip install nltk

## How to use the app?

After installing the required modules, the user can run the file "interface.py" by any python2 compiler. And the interface should be self-explanatory about how to proceed.
