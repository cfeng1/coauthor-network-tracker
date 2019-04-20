# coding=utf-8
# python 2
# author: Chi Faith Feng

from Tkinter import *
from ttk import *
import tkFileDialog
import tkMessageBox
import os, re, random, copy
from searchAndCheckUrl import *
from extractInfoFromFile import *
from helpers import *

##################################################################
############################## HELPERS ###########################
##################################################################
def ButtonPress(event, canvas):
    # dragging nodes:
    # http://stackoverflow.com/questions/6740855/
    # board-drawing-code-to-move-an-oval/6789351#6789351
    x, y = event.x, event.y
    Main.dragData["item"] = canvas.find_closest(x, y)[0]
    Main.dragData["x"] = x
    Main.dragData["y"] = y
    for node in Data.nodesLoc:
        cx, cy = Data.nodesLoc[node]
        if ((x-cx)**2.0+(y-cy)**2.0)**0.5<=5:
            Main.dragData["node"] = node

def ButtonRelease(event, canvas):
    Main.dragData["item"] = None
    Main.dragData["x"] = 0
    Main.dragData["y"] = 0
    Main.dragData["node"] = None

def MoveButton(event, canvas):
    dx = event.x - Main.dragData["x"]
    dy = event.y - Main.dragData["y"]
    canvas.move(Main.dragData["item"], dx, dy)
    Main.dragData["x"] = event.x
    Main.dragData["y"] = event.y
    node = Main.dragData["node"]
    Data.nodesLoc[node] = (event.x, event.y)

def doubleClickRemove(event):
    x, y = event.x, event.y
    if Data.nodesLoc!=None and len(Data.nodesLoc)!=0:
        temp = copy.copy(Data.nodesLoc)
        for node in temp:
            if node in Data.nodesLoc.keys():
                cx, cy = Data.nodesLoc[node]
                dis = ((cx-x)**2.0+(cy-y)**2.0)**0.5
                if dis<10:
                    Data.network.removeNode(node)
                    del Data.nodesLoc[node]

def hover(event, canvas, network, size):
    # nodesLoc = Data.nodesLoc
    if len(network.nodes)!=0 and Data.nodesLoc!=None:
        x,y = event.x, event.y
        drawNetwork(canvas, network, size)
        for node in network.nodes:
            if node in Data.nodesLoc:
                nx, ny = Data.nodesLoc[node]
                dis = ((nx-x)**2.0+(ny-y)**2.0)**0.5
                if dis<10:
                    text = network.nodeAttrs[node]
                    if text == None: text = "nan"
                    elem = canvas.create_text(x, y-10, text=text,
                                            font="Arial 12 bold")

def drawNetwork(canvas, network, size):
    paleBlue = rgbString(175,238,238)
    slate = rgbString(112,128,144)
    smoke = rgbString(230,230,230)
    nodesLoc = Data.nodesLoc
    if Data.noResult==False and len(network.nodes)!=0 and nodesLoc!=None:
        canvas.delete("all")
        canvas.create_rectangle(0,0,size,size,fill=smoke)
        drawEdges(canvas, network.edges, Data.nodesLoc, color=slate)
        drawNodes(canvas, Data.nodesLoc, size, size, color=paleBlue)
        canvas.create_text(size*0.5, size*0.05,
            text="Drag a node to move, double click to remove",
            fill=slate, font="Arial 14 bold")
        canvas.create_text(size*0.5, size*0.95,
                    text="Hover to view PhD graduation year",
                    fill=slate, font="Arial 14 bold")
        Analysis.highlightShortestPath(Analysis.shortestPath,
                                        Data.nodesLoc, canvas)
    elif Data.noResult==True:
        canvas.create_text(size*0.5, size*0.5, text="No CV Found...", 
                    fill="blue", font="Arial 20 bold")

##################################################################
############################## GUI ###############################

class Main(Tk):
    dragData = {"x":0, "y":0, "item":None, "node":None}
    def __init__(self, *args, **kwargs):
        root = Tk.__init__(self, *args, **kwargs)
        window = Frame(self)
        window.pack(side=TOP, fill="both", expand=True)
        window.grid_rowconfigure(0, weight=1)
        window.grid_columnconfigure(0, weight=1)
        self.frames = dict()
        for frame in (Starter, Data, Analysis):
            page = frame(window, self)
            self.frames[frame] = page
            page.grid(row=0, column=0, sticky="nsew")
        self.show(Starter)
    def show(self, page):
        frame = self.frames[page]
        frame.tkraise()

####  Start Mode
class Starter(Frame):
    def __init__(self, window, control):
        Frame.__init__(self, window)
        # graph instruction
        size = Data.size*0.9
        canvas = Canvas(self, width=size, height=size)
        drawRandomNetwork(size=size, num=14, canvas=canvas)
        canvas.pack()
        filler = Label(self, text="\t")
        filler.pack()
        start = Button(self, text="Start!",
                        command=lambda: control.show(Data))
        start.pack()

####  DATA MODE
class Data(Frame):
    row, size = 0, 500
    noResult = None
    network = Network()
    nodesLoc = None
    visitedProfile = dict()
    @staticmethod
    def findIndirectCoauthors(name, field, network, depth=0):
        # python2 does not have "nonlocal"
        def findCV(name, field, stop=5):
            # Data.visitedProfile is a dictionary of dictionary
            if ((name in Data.visitedProfile) and
                (Data.visitedProfile[name]["profile"]!=None)):
                # print "visited!!!"
                return (Data.visitedProfile[name]["url"],
                        Data.visitedProfile[name]["profile"])
            keywords = [name, field, "CV"]
            query = " ".join(keywords)
            lastName = lowerLastName(name)
            searchResults = googleSearch(query, stop=stop)
            allVisitedURLs = []
            if len(Data.visitedProfile)!=0:
                for name in Data.visitedProfile:
                    # print "dictionary", name, Data.visitedProfile[name]
                    if Data.visitedProfile[name]["url"]!=None:
                        allVisitedURLs.append(Data.visitedProfile[name]["url"])
            for url in searchResults:
                if url not in allVisitedURLs:
                    pdfRes = isValidPdfURL(url, name)
                    if pdfRes != None:
                        return (url, pdfRes)
                    htmlRes = isValidHtmlURL(url, name)
                    if htmlRes != None:
                        return (url, htmlRes)
                    # check links hidden in a personal webpage
                    otherResult = searchPdfLink(url, name)
                    if otherResult != None:
                        (url, profile) = otherResult
                        return (url, profile)

        def findDirectCoauthors(authorName, field, network):
            authorName = joinFullName(authorName.split())
            authorLastName = lowerLastName(authorName)
            res = findCV(authorName, field)
            if res!=None:
                try:
                    authorUrl, authorProfile = res
                except:
                    print "direct coauthos result", res
                authorYear = phdYear(authorProfile)
                if authorYear == None: authorYear = "nan"
                network.addNode(authorName, authorYear)
                results = possibleCoauthorsAndCombo(authorProfile)
                if results!=None:
                    coauthors, combos = results
                    for coauthorName in list(coauthors):
                        coauthorName = joinFullName(coauthorName.split())
                        if coauthorName!=None:
                            res = findCV(coauthorName, field)
                            if res!=None:
                                coauthorUrl, coauthorProfile = res
                                temp = {"url": coauthorUrl, "profile": coauthorProfile}
                                Data.visitedProfile[coauthorName] = temp
                                if coauthorProfile == None:
                                    network.addNode(coauthorName, "nan")
                                    network.addEdge(authorName,coauthorName)
                                else:
                                    coauthorYear = phdYear(coauthorProfile)
                                    if coauthorYear == None: coauthorYear = "nan"
                                    network.addNode(coauthorName,coauthorYear)
                                    network.addEdge(coauthorName,authorName)
                    for combo in combos:
                        node1, node2 = combo
                        network.addEdge(node1, node2)
        ################## Recursion Part ################
        if depth<0 or len(name)==0: return None
        elif depth == 0:
            findDirectCoauthors(name, field, network)
            return list(network.edges[name])
        else:
            findDirectCoauthors(name, field, network)
            directCoauthors = network.edges[name]
            if directCoauthors != None:
                for coauthorName in directCoauthors:
                    lastName = lowerLastName(coauthorName)
                    Data.findIndirectCoauthors(coauthorName, field,
                                            network, depth-1)
                return list(network.edges[name])

    def instructions(self, instructions):
        # span 4 columns in layout
        cols = 4
        for text in instructions:
            row = Data.row + 1
            ins = Label(self, text=text)
            ins.grid(row=row, column=0, columnspan=cols, pady=5, sticky=N)
            Data.row = row

    entries = tuple()
    def forms(self):
        # span 2 columns
        cols = 2
        font = ("Arial", 12)
        fields = ("Full Name: ", "Research Field: ",
            "Coauthor Radius: ")
        entries = []
        for field in fields:
            row = Data.row + 1
            lab = Label(self, text=field, font=font)
            lab.grid(row=row, column=0, columnspan=2, pady=5)
            entry = Entry(self)
            entry.grid(row=row, column=2, columnspan=2, pady=5)
            entries.append(entry)
            Data.row = row
        Data.entries = entries

    directory = ""
    def chooseDir(self):
        filename = tkFileDialog.asksaveasfilename(**self.file_opt)
        Data.directory = filename
        path, file = sepPathFile(Data.directory)
        if path=="":
            print "No directory selected!"
        else:
            network = Data.network
            curDir = os.getcwd()
            os.chdir(path)
            tempFile = open(file, 'w')
            tempFile.write("name; phd graduation year; coauthors \n")
            if network.nodes!=None and len(network.nodes)!=0:
                for node in network.nodes:
                    entry = node + ";"
                    if network.nodeAttrs[node]!=None:
                        entry += str(network.nodeAttrs[node]) + ";"
                    else: entry += "nan;"
                    if network.edges[node]!=None:
                        entry += str(network.edges[node])
                    else: entry += "nan"
                    tempFile.write(entry+"\n")
            tempFile.close()
            os.chdir(curDir)

    @staticmethod
    def createNetwork(entries):
        Data.noResult = False
        Data.network = Network()
        information = []
        for entry in entries:
            text = entry.get()
            if text!="":
                information.append(text)
        if len(information)==3:
            tkMessageBox.showinfo("Sit Tight and Be Patient :)", 
            "Hit OK to begin generating... It will take a minute or two")
            """
            ## Testing graphics
            def setNetwork(network):
              nodes = ["A", "B", "C", "D", "E"]
              attrs = [1997, 2002, 2010, 1988, 1979]
              edges = [("A", "B"), ("A", "C"), ("B", "E"), ("D", "E")]
              for i in range(len(nodes)):
                  nodeName = nodes[i]
                  nodeAttr = attrs[i]
                  network.addNode(nodeName, nodeAttr)
              for j in range(len(edges)):
                  node1, node2 = edges[j]
                  network.addEdge(node1, node2)
            Data.network = Network()
            setNetwork(Data.network)
            print Data.network.nodes
            print Data.network.nodeAttrs
            """
            name, field, depth = information
            Data.depth = int(float(depth))
            # print Data.depth
            Data.findIndirectCoauthors(name, field, 
                        network=Data.network, depth=Data.depth)
            
            if len(Data.network.nodes)!=0:
                Data.nodesLoc = scatterNodes(Data.network.nodes,
                                    Data.size, Data.size)
            else:
                Data.noResult = True
                # https://www.tutorialspoint.com/python/tk_messagebox.htm
                tkMessageBox.showinfo("No Result", "No Valid CV Found :(")
        else:
            tkMessageBox.showinfo("Need More Information", 
                        "Please enter all information to generate the network")

    @staticmethod
    def clearAll(entries):
        for entry in entries:
            entry.delete(0, END)

    @staticmethod
    def loadNetwork(networkData):
        Data.noResult = False
        Data.network = Network()
        lines = networkData.splitlines()
        for line in lines[1:len(lines)]:
            items = line.strip().split(";")
            if len(items)==3:
                name = items[0]
                phdYear = items[1]
                Data.network.addNode(name, phdYear)
                # exclude [] at the beginning and end
                coauthors = items[2][1:-1]
                coauthors = coauthors.split(",")
                # exclude '' at the beginning and end
                coauthors=[coauthor.strip()[1:-1] for coauthor in coauthors]
                for coauthor in coauthors:
                    Data.network.addEdge(name, coauthor)
        if len(Data.network.nodes)!=0:
            Data.nodesLoc = scatterNodes(Data.network.nodes,
                                Data.size, Data.size)
            drawNetwork(Data.canvas, Data.network, Data.size)

    def upload(self):
        fileName = tkFileDialog.askopenfilename(**self.file_opt)
        if fileName:
            file = open(fileName, 'r')
            networkData = file.read()
            file.close()
            Data.loadNetwork(networkData)

    def buttons(self):
        Data.row = Data.row + 1
        clear = Button(self, text="Clear All",
            command=lambda e=Data.entries: Data.clearAll(e))
        clear.grid(row=Data.row, column=2, pady=5)
        self.generate = Button(self, text="Generate",
            command=lambda e=Data.entries: Data.createNetwork(e))
        self.generate.grid(row=Data.row, column=3, pady=5)

        upload = Button(self, text="Upload", command=self.upload)
        upload.grid(row=Data.row+1, column=2, pady=5)
        path = Button(self, text="Save To", command=self.chooseDir)
        path.grid(row=Data.row+1, column=3, pady=5)
        Data.row = Data.row + 1

    def __init__(self, window, control):
        self.window = window
        Frame.__init__(self, window)
        analysis = Button(self, text="Analysis Mode",
                    command=lambda: control.show(Analysis))
        analysis.grid(row=0, column=0, columnspan=2, pady=5)
        instructions = [
                "Enter information and hit 'Generate'!",
                "Generating network may take a while"]
        self.instructions(instructions)
        self.forms()
        # http://tkinter.unpythonic.net/wiki/tkFileDialog
        self.file_opt = options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('text files', '.txt')]
        options['initialdir'] = os.getcwd()
        options['initialfile'] = 'networkData.txt'
        options['parent'] = self
        options['title'] = "networkData.txt"
        self.cancel_id = None
        self.buttons()
        ## graph
        paleBlue = rgbString(175,238,238)
        smoke = rgbString(230,230,230)
        size = Data.size
        canvas = Canvas(self, width=size, height=size)
        Data.canvas = canvas
        canvas.grid(row=0, column=8, columnspan=20, rowspan=12)
        canvas.create_rectangle(0,0,size,size,fill=smoke,width=0)
        canvas.create_text(size*0.5, size*0.1, fill="navy",
                text="Coauthor Network Tracker", font="Arial 24 bold")
        canvas.create_text(size*0.5, size*0.45, fill="navy",
                text="Enter the name, research field and ", font="Arial 20")
        canvas.create_text(size*0.5, size*0.5, fill="navy",
                text="coauthor radius* to generate the network!", font="Arial 20")
        canvas.create_text(size*0.5, size*0.55, fill="navy",
                text="Come back later, then hover to update the graph!", font="Arial 20")
        canvas.create_text(size*0.5, size*0.85, fill="blue",
                text="*Note: if coauthor radius is 0, then only collect direct coauthors;", 
                font="Arial 16")
        canvas.create_text(size*0.5, size*0.9, fill="blue",
                text="if coauthor radius is 1, then collect coauthors' coauthors.", 
                font="Arial 16")
        canvas.create_text(size*0.5, size*0.95, fill="blue",
                text="Only nonnegative integers are allowed.", 
                font="Arial 16")
        # inspired by class notes
        canvas.bind("<Motion>", lambda event:
                        hover(event, canvas, Data.network, size))
        canvas.bind("<Double-Button-1>", lambda event:
                    doubleClickRemove(event))
        canvas.tag_bind("node", "<ButtonPress-1>", lambda event:
                        ButtonPress(event, canvas))
        canvas.tag_bind("node", "<ButtonRelease-1>", lambda event:
                        ButtonRelease(event, canvas))
        canvas.tag_bind("node", "<B1-Motion>", lambda event:
                        MoveButton(event, canvas))

##################################################################
####  Analysis Mode
class Analysis(Frame):
    shortestPath = None
    @staticmethod
    def findShortestPaths(entries, networkEdges, nodesLoc, canvas):
        # find all shortest paths, but only draw one
        if len(entries)==2:
            temp = []
            for entry in entries:
                temp.append(entry.get())
            if (len(temp)==2):
                start, end = temp[0], temp[1]
            allPaths = []
            def paths(networkEdges, start, end, visited):
                if end in visited:
                    allPaths.append(visited)
                else:
                    directNodes = networkEdges[start]
                    for node in directNodes:
                        if (node in Data.nodesLoc and node not in visited):
                            temp = visited + [node]
                            res = paths(networkEdges, node, end, temp)
            # highlight one shortest path
            if (start in networkEdges and end in networkEdges):
                paths(networkEdges, start, end, visited=[start])
                f = lambda x: len(x)==min(map(len, allPaths))
                shortestPaths = filter(f, allPaths)
                Analysis.shortestPath = shortestPaths[0]
                Analysis.highlightShortestPath(Analysis.shortestPath,
                                                    nodesLoc,canvas)
    @staticmethod
    def highlightShortestPath(path, nodesLoc, canvas):
        if path != None and len(path) != 0:
            for ind in range(1, len(path)):
                node0, node1 = path[ind-1], path[ind]
                x0, y0 = nodesLoc[node0]
                x1, y1 = nodesLoc[node1]
                canvas.create_line(x0,y0,x1,y1,fill="green",width=2)
        paleBlue = rgbString(175,238,238)
        drawNodes(canvas, nodesLoc, Data.size, Data.size, color=paleBlue)
    
    row = 0
    def instructions(self, instructions):
        cols = 4
        for text in instructions:
            row = Analysis.row + 1
            ins = Label(self, text=text) #, fg=color, font=font
            ins.grid(row=row, column=0, columnspan=cols, pady=5, sticky=N)
            Analysis.row = row

    entries = tuple()
    def forms(self):
        # span 2 columns
        cols = 2
        font = ("Arial", 12)
        fields = ("Start: ", "End: ")
        entries = []
        for field in fields:
            row = Analysis.row + 1
            lab = Label(self, text=field, font=font)
            lab.grid(row=row, column=0, columnspan=2, pady=5)
            entry = Entry(self)
            entry.grid(row=row, column=2, columnspan=2, pady=5, padx=10)
            entries.append(entry)
            Analysis.row = row
        Analysis.entries = entries

    def clearAll(self, entries):
        for entry in entries:
            entry.delete(0, END)
        Analysis.shortestPath = None

    def buttons(self):
        Analysis.row = Analysis.row + 1
        fill1 = Label(self, text="   ")
        fill1.grid(row=Analysis.row, column=0, pady=5)
        generate = Button(self, text="Generate",
            command=lambda e=Analysis.entries: Analysis.findShortestPaths(e,
            Data.network.edges, Data.nodesLoc, self.canvas))
        generate.grid(row=Analysis.row, column=2, pady=5)
        clear = Button(self, text="Clear All",
            command=lambda e=Analysis.entries: self.clearAll(e))
        clear.grid(row=Analysis.row, column=3, pady=5)

    def __init__(self, window, control):
        Frame.__init__(self, window)
        analysis = Button(self, text="Data Mode",
                    command=lambda: control.show(Data))
        analysis.grid(row=0, column=0, columnspan=2, pady=5)
        instructions = [
                "Enter two researchers\' names to find",
                "the shortest path between them! "]
        self.instructions(instructions)
        self.forms()
        self.buttons()
        # graph
        network = Data.network
        paleBlue = rgbString(175,238,238)
        smoke = rgbString(230,230,230)
        size = Data.size
        canvas = Canvas(self, width=size, height=size)
        self.canvas = canvas
        canvas.grid(row=0, column=8, columnspan=20, rowspan=12)
        canvas.create_rectangle(0,0,size,size,fill=smoke,width=0)
        canvas.create_text(size*0.5, size*0.1, fill="navy",
                text="Coauthor Network Tracker", font="Arial 24 bold")
        canvas.create_text(size*0.5, size*0.45, fill="navy",
                text="Hover to check the visualize the network!", font="Arial 20")
        canvas.create_text(size*0.5, size*0.5, fill="navy",
                text="Click GENERATE to highlight ", font="Arial 20")
        canvas.create_text(size*0.5, size*0.55, fill="navy",
                text="the shortest path between any two nodes", font="Arial 20")
        # inspired by class notes
        canvas.bind("<Motion>", lambda event:
                        hover(event, canvas, Data.network, size))
        canvas.bind("<Double-Button-1>", lambda event:
                        doubleClickRemove(event))

if __name__=="__main__":
    app = Main()
    app.mainloop()