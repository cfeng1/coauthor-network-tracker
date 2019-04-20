# coding=utf-8
# python 2
# author: Chi Faith Feng

from google import search as googleSearch
import urllib2, requests, re, string
from bs4 import BeautifulSoup
from unidecode import unidecode
from helpers import *
from extractInfoFromFile import *

def dropBoxPdf(url):
	# pdf in dropbox
	# based on: http://www.xavierdupre.fr/blog/2015-01-20_nojs.html
	if url.endswith("?dl=0"):
		url = url[:-1]+"1"
	elif url.endswith("?dl=0"): pass
	else: url += "?dl=1"
	try:
		r = requests.get(url)
		return r
	except:
		return None

def otherPdfFiles(url, lastName):
	profile = pdfToText(url)
	if profile!=None:
		if lastName.lower() not in profile.lower():
			return None
		pub = r'publication.|published.|research\spapers'
		pubPat = re.compile(pub, flags=re.I|re.M)
		resPub = re.findall(pubPat, profile)
		phdPat = re.compile(r'ph\.?d\.?', flags=re.I|re.M)
		resPhd = re.findall(phdPat, profile)
		if (len(resPub)>0 and len(resPhd)>0): return profile
	else: return None

def isValidPdfURL(url, name):
	if not url.startswith("http"): return None
	cvPat = re.compile(r'cv|resume|curri\.*vita\.*', flags=re.I|re.M)
	cvRes = cvPat.findall(url)
	if url.startswith("http"):
		if len(cvRes) == 0: return None
	try:
		r = requests.get(url)
	except:
		return None
	if not ("dropbox" in url):
		if not ("pdf" in r.headers["content-type"]):
			return None
	else:
		res = dropBoxPdf(url)
		if res==None: return None
	lastName = name.split()[-1]
	if "-" in lastName: lastName = name.split("-")[-1]
	if len(cvRes)>0:
		# quick qualifier: both last name and cv in url
		if lastName in url:
			res = pdfToText(url)
			if res==None: return None
			else: return res
	else:
		if "docs.google" not in url: return None
	try:
		return otherPdfFiles(url, lastName)
	except:
		return None

def locateSlash(url):
	slashPat = re.compile(r'/')
	locations = []
	for elem in slashPat.finditer(url):
		locations.append(elem.start())
	return locations[1:]

def prependPDFLink(url, link, name):
	segmentLink = link.split("/")
	for ind in range(len(segmentLink)):
		elem = segmentLink[ind]
		if not (len(elem)==0 or elem in string.whitespace):
			startSeg = elem
			break
		else: startSeg = None
	if (isinstance(startSeg, str) and startSeg in url):
		# find the last place with start
		lastLoc = url.rfind(startSeg)
		prefix = url[:lastLoc]
		fullLink = prefix+link
		res = isValidPdfURL(fullLink, name)
		if res!=None:
			return (fullLink, res)
	else:
		if not url.endswith("/"):
			url += "/"
		slashLoc = locateSlash(url)
		for ind in range(len(slashLoc)-1,-1,-1):
			sLoc = slashLoc[ind]
			tempLink = url[:sLoc]+"/"+link
			res = isValidPdfURL(tempLink, name)
			if res!=None:
				return (tempLink, res)
	return None

def searchPdfLink(url, name):
	# return pdf url
	try:
		page = urllib2.urlopen(url)
		soup = BeautifulSoup(page, "lxml")
		hrefs = soup.find_all("a")
		links = [link.get("href") for link in hrefs]
		for link in links:
			if (isinstance(link, str) and len(link)>1):
				res = isValidPdfURL(link, name)
				if res!=None:
					return (link, res)
				else:
					if not link.startswith("#"):
						res = prependPDFLink(url, link, name)
						if res != None:
							link, profile = res
							return (link, profile)
		return None
	except: return None

def HtmlToText(url):
	try:
		page = urllib2.urlopen(url)
		soup = BeautifulSoup(page, "lxml")
		text = soup.get_text()
		text = unidecode(text)
		return text
	except:
		return None

def isValidHtmlURL(url, name):
	# need to exclude university faculty page?
	lastName = name.split()[-1].lower()
	if "-" in lastName:
		lastName = name.split("-")[-1]
	if lastName.lower() not in url.lower():
		return None
	parsed = HtmlToText(url)
	if parsed==None: return None
	if lastName not in parsed: return None
	pub = r'publication.|published.|research\spapers'
	pubPat = re.compile(pub, flags=re.I|re.M)
	resPub = re.findall(pubPat, parsed)
	phdPat = re.compile(r'ph\.?d\.?', flags=re.I|re.M)
	resPhd = re.findall(phdPat, parsed)
	if (len(resPub)>0 and len(resPhd)>0):
		return parsed
	else: return None

