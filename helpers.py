# coding=utf-8
# python 2
# author: Chi Faith Feng

import os, re, random, copy
# Data structure: how I represent network (inspired by networkx)
class Network(object):
	# inspired by networkx (except for edges)
	def __init__(self):
		self.nodes = set()
		self.edges = dict()
		self.nodeAttrs = dict()
	
	def addNode(self, node, attr=None):
		self.nodes.add(node)
		self.nodeAttrs[node] = attr

	def addEdge(self, node1, node2):
		for node in [node1, node2]:
			self.nodes.add(node)
			attr = self.nodeAttrs.get(node)
			if attr == None:
				self.nodeAttrs[node] = None
		self.edges[node1] = self.edges.get(node1,[])+[node2]
		self.edges[node2] = self.edges.get(node2,[])+[node1]

	def removeNode(self, node1):
		if node1 in self.nodes:
			self.nodes.remove(node1)
			del self.nodeAttrs[node1]
		if node1 in self.edges:
			del self.edges[node1]
		for node0 in self.edges:
			if node1 in self.edges[node0]:
				self.edges[node0].remove(node1)

# Helper functions
def sepPathFile(filepath):
	if not os.path.isdir(filepath):
		temp = filepath.split("/")
		path = "/".join(temp[0:len(temp)-1])
		file = temp[-1]
		return (path, file)

def rgbString(red, green, blue):
	# from 112 class notes
	return "#%02x%02x%02x" % (red, green, blue)

def floatGrid(start, end, step):
	res = []
	x = start
	while x<=end:
		res.append(x)
		x += step
	return res

def scatterNodes(nodes, width, height):
	nodes = list(nodes)
	nodesLoc = dict()
	numNodes = len(nodes)
	nodeSize = min(width, height)/(2.0*numNodes)
	seen = set()
	for i in range(numNodes):
		node = nodes[i]
		xGrids = floatGrid(nodeSize, width-nodeSize, nodeSize)
		yGrids = floatGrid(nodeSize, height-nodeSize, nodeSize)
		cxInd = random.randrange(0,len(xGrids))
		cyInd = random.randrange(0,len(yGrids))
		cx, cy = xGrids[cxInd], yGrids[cyInd]
		while (cxInd, cyInd) in seen:
			cxInd = random.randrange(0,len(xGrids))
			cyInd = random.randrange(0,len(yGrids))
			cx, cy = xGrids[cxInd], yGrids[cyInd]
		seen.add((cxInd,cyInd))
		nodesLoc[node] = (cx, cy)
	return nodesLoc

def drawNodes(canvas, nodesLoc, width, height, color="gray"):
	numNodes = len(nodesLoc)
	# r = (min(width, height)/(2.0*numNodes))/4
	r = 8
	for node in nodesLoc:
		cx, cy = nodesLoc[node]
		canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=color, 
										width=0)
		canvas.create_text(cx, cy, text=node, font="Arial 10 bold", 
										tags="node")
	return r

def drawEdges(canvas, edges, nodesLoc, color="black"):
	temp = []
	for node0 in edges:
		if node0 in nodesLoc:
			links = edges[node0]
			for node1 in links:
				if ((node1 in nodesLoc) and ((node0, node1) not in temp)
									 and ((node1, node0) not in temp)):
					temp.append((node0, node1))
					cx0, cy0 = nodesLoc[node0]
					cx1, cy1 = nodesLoc[node1]
					canvas.create_line(cx0, cy0, cx1, cy1, fill=color)

def drawRandomNetwork(size, num, canvas):
	paleBlue = rgbString(175,238,238)
	smoke = rgbString(230,230,230)
	slate = rgbString(112,128,144)
	canvas.create_rectangle(-5,-5,size+10,size+10,fill=smoke,width=0)
	nodes = [chr(i) for i in range(ord("A"), ord("A")+num)]
	nodesLoc = scatterNodes(nodes,size,size)
	edges = dict()
	for node in nodes:
		indLink = random.randint(1,num-1)
		edges[node] = nodes[indLink]
	drawEdges(canvas, edges, nodesLoc, color=slate)
	for node in nodesLoc:
		cx, cy = nodesLoc[node]
		r = random.randint(num*0.5, num)
		canvas.create_oval(cx-r,cy-r,cx+r,cy+r,fill=paleBlue,width=0)
	instructions = ["This app helps you find the coauthor network",
					"\n", "of any researcher without any database!",
					"\n", "All you need is the internet connection!",
					"\n", "Click 'Start' to begin!"]
	gap = 30
	row = size*0.5-size*0.15
	for text in instructions:
		canvas.create_text(size*0.5, row, text=text, 
							fill="navy", font="Arial 16 bold")
		row += gap

#############################################
# 1. given a pdf url, turn it into string
# based on the answer by user3272884:
# http://stackoverflow.com/questions/25665/python-module-for-converting-pdf-to-text
# and answer by John:
# http://stackoverflow.com/questions/9751197/opening-pdf-urls-with-pypdf
#############################################
import sys
import string
from unidecode import unidecode
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.layout import LAParams
from cStringIO import StringIO
from urllib2 import Request, urlopen

def pdfToText(url):
    result = ""
    try:
        remoteFile = urlopen(Request(url)).read()
    except:
        raise Exception("Invalid Url")
    remoteFile = urlopen(Request(url)).read()
    memoryFile = StringIO(remoteFile)
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Process each page contained in the document.
    try:
        for page in PDFPage.get_pages(memoryFile):
            interpreter.process_page(page)
            data =  retstr.getvalue()
        # convert special characters to closest ascii
        result = result + data
        result = result.decode('utf-8')
        file = unidecode(result)
        return file
    except:
        return None