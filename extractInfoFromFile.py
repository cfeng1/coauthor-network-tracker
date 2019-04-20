# coding=utf-8
# python 2
# author: Chi Faith Feng

import nltk
import re, itertools
from searchAndCheckUrl import *

def lowerLastName(name):
    return name.split()[-1].lower()

def nameFormatting(firstName):
    return firstName[0].upper()+firstName[1:].lower()

def joinFullName(fullNameList):
    if len(fullNameList)==0:
        return ""
    elif len(fullNameList)==1:
        return nameFormatting(fullNameList[0])
    else:
        name = fullNameList[0]
        for ind in range(1, len(fullNameList)):
            temp = nameFormatting(fullNameList[ind])
            if name[-1].isalpha():
                name += " "+temp
            else: name += temp
        return name

def findYear(line):
    import datetime
    currentYear = datetime.datetime.now().year
    yearPat = re.compile(r'\d{4}')
    results = yearPat.finditer(line)
    years = []
    for elem in results:
        years.append(elem.group())
    if len(years)==1: return years[0]
    elif len(years)>1:
        maxYear = None
        for i in range(len(years)):
            year = years[i]
            if year<=currentYear:
                if maxYear==None or year>maxYear:
                    maxYear = year
        return maxYear
    else: return None

def phdYear(profile):
    # search for term "PHD", find the closest year
    profile = profile.lower()
    # pattern: ph(space or point or nothing)d(space or point or nothing)
    # deal with multiple terms of phd in the text
    phdPat1 = re.compile(r'ph\.?d\.?', flags=re.I|re.M)
    phdPat2 = re.compile(r'ph\s?d\s?', flags=re.I|re.M)
    items = set()
    startItems = []
    for PHDpattern in [phdPat1, phdPat2]:
        for elem in PHDpattern.finditer(profile):
            item = elem.group()
            items.add(item)
            length = len(item)
            start = elem.start()
            startItems.append((start, item))
    for line in profile.splitlines():
        for phdItem in list(items):
            if phdItem in line:
                # year in the same line as PHD, return it
                year = findYear(line)
                if year!=None: return year
    yearPat = re.compile(r'\d{4}')
    years = yearPat.finditer(profile)
    yearDis = []
    for startItem in startItems:
        start, item = startItem
        minDistance = None
        minYear = None
        for year in years:
            loc = year.start()
            dis = abs(loc-start)
            if minDistance==None or dis<minDistance:
                minDistance = dis
                minYear = year.group()
        if minDistance!=None and minYear!=None:
            yearDis.append((minDistance, minYear))
    if len(yearDis)==0: return None
    elif len(yearDis)==1: return yearDis[0][1]
    else:
        minDis, minYear = yearDis[0]
        for i in range(1, len(yearDis)):
            dis, year = yearDis[i]
            if dis<minDis: minDis, minYear = dis, year 
        return minYear

def findPublications(resume):
    startPat = re.compile(r'publication.|published.', 
                            flags=re.I|re.M)
    endPat = re.compile(r'working paper.', flags=re.I|re.M)
    startIter = startPat.finditer(resume)
    endIter = endPat.finditer(resume)
    count = 0
    iters = itertools.izip(startIter, endIter)
    (startInd, startLen, endLen) = (None, None, None)
    for (s, e) in iters:
        count+=1
        startInd = s.start()
        endInd = e.start()
        startWord, endWord = s.group(), e.group()
        startLen, endLen = len(startWord), len(endWord)
        if count>0: break
    if (startInd, startLen, endLen) != (None, None, None):
        publications = resume[startInd+startLen:endInd].strip()
        return publications
    else: return None

def possibleCoauthorsAndCombo(profile):
    # extract possible coauthors and links among coauthors
    publicationSection = findPublications(profile)
    if publicationSection != None:
        sents = nltk.sent_tokenize(publicationSection)
        directCoauthors = set()
        combos = set()
        for sent in sents:
            # getting rid of book editors:
            # ignore lines with "edit" in it
            if not ("edit" in sent.lower()):
            # go by each publication (line by line)
                words = nltk.word_tokenize(sent)
                tree = nltk.ne_chunk(nltk.pos_tag(words), binary=False)
                tempAuthors = set()
                for elem in tree:
                    if isinstance(elem, nltk.tree.Tree):
                        if elem.label()=="PERSON" and len(elem.leaves())==2:
                            fullNameList = [l[0] for l in elem.leaves()]
                            name = joinFullName(fullNameList)
                            tempAuthors.add(name)
                            directCoauthors.add(name)
                if len(tempAuthors)>1:
                    for item in list(itertools.combinations(tempAuthors,2)):
                        combos.add(item)
        return (directCoauthors, combos)
    else: return None

## test
# import os
# os.chdir("/Users/chifeng/Downloads")
# file = open("temp.txt","r")
# cv = file.read()
# file.close()
# print phdYear(cv)

