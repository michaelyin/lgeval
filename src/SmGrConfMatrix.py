# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 05:56:16 2013

@author: Harold
"""
from operator import itemgetter

class SmDict(object):
	"""This is a real dictionnary but it is like a dictionnary using only 
	the == operator (without hash) 
	A value can be associate to a smallGraph. 
	For efficiency, use an object as a value to avoid call to set()
	It uses the isomorphism to know if 2 smallGraphh are the same."""
	
	
	def __init__(self,*args):
		self.myitems = []
		
	def set(self, sg, value):
		for i in range(len(self.myitems)):
			if(sg == self.myitems[i][0]):
				self.myitems[i][1] = value
				return
		self.myitems.append((sg,value))
		
	def get(self, sg, defaultType = object):
		"""find the corresponding key and if not found add it with the default value"""
		for i in range(len(self.myitems)):
			if(sg == self.myitems[i][0]):
				return self.myitems[i][1]
		self.myitems.append((sg, defaultType()))
		return self.myitems[-1][1]
		
	def __contains__(self,sg):
		for i in range(len(self.myitems)):
			if(sg == self.myitems[i][0]):
				return True
		return False

	def getIter(self):
		for p in self.myitems:
			yield p
	def __str__(self):
		res = "{"
		for (k,v) in self.myitems:
			res = res + "(" + str(k) + ":" + str(v) + "),"
		return res[:-1] + "}"
	def toHTML(self):
		html = '<table border="1">\n'
		for (g,v) in self.myitems:
			html = html + '<tr><td>\n' + g.toSVG(100) + '</td>\n'
			html = html + '<td>'+str(v)+'</td></tr>\n'
		return html + '</table>\n'
		

class Counter(object):
	""" just a small counter but embedded in an object
	Designed to be used in smDict
        It can save a list of object by adding it as param in the 
        incr() function"""
	
	def __init__(self,*args):
		self.value = 0
                self.list = []
                if(len(args)> 0):
                        self.value = int(args[0])
                        if (len(args) == 2):
                                self.list = args[1]
	def incr(self,elem=None):
		self.value = self.value +1
                if elem != None:
                        self.list.append(elem)
	def get(self):
		return self.value
	def set(self,v):
		self.value = int(v)
        def getList(self):
                return self.list
        def add(self,c2):
                return Counter(self.value + c2.value, self.list + c2.list)

        def __add__(self,c2):
                return Counter(self.value + c2.value, self.list + c2.list)

	def __str__(self):
		return str(self.value)
	def __int__(self):
		return self.value
	
	
	
class ConfMatrix(object):
	
	def __init__(self,*args):
		self.mat = SmDict()
	
	def incr(self, row, column,elem=None):
                """ add 1 (one) to the counter indexed by row and column
                an object can be added in the attached list"""
		self.mat.get(row, SmDict).get(column,Counter).incr(elem)
	def __str__(self):
		return str(self.mat)
	def toHTMLfull(self, outputStream):
		i = 0
		allErr = SmDict()
		outputStream.write(' <table border="1"><tr>')
		outputStream.write('<td></td>')
		for (rowG,col) in self.mat.getIter():
			for (g,_) in col.getIter():
				c = allErr.get(g,Counter)
				if c.get() == 0:
					c.set(i)
					i = i+1
					outputStream.write( '<th>' + g.toSVG(100) + '</th>')
		outputStream.write('</tr>')
		nbE = len(allErr.myitems)
		for (rowG,col) in self.mat.getIter():
			i = 0
			outputStream.write('<tr><th>\n' + rowG.toSVG(100) + '</th>')
			for (g,v) in col.getIter():
				c = allErr.get(g)
				for empty in range(i,c.get()):
					outputStream.write('   <td>0</td>')
				outputStream.write('   <td>' + str(v) + '</td>')
				i = c.get()
			for empty in range(i,nbE-1):
				outputStream.write('   <td>0</td>')
			outputStream.write('</tr>\n')
		outputStream.write('</table>\n<p>')

	def toHTML(self, outputStream, limit = 0, viewerURL=""):
                """ write in the output stream the HTML code for this matrix and
                return a Counter object with
                the number of non shown errors and the list of hidden elements
                The list of files with error is prefixed with the param viewerURL
                in the href attribute."""
		outputStream.write(' <table border="1"><tr>')
		arrow = True
		hiddenErr = Counter()
		sortedList = []
                # first count all error for each sub structure
		for (rowG,col) in self.mat.getIter():
			nbE = sum([v for (_,v) in col.getIter()],Counter())
			sortedList.append((rowG,col,nbE))
		sortedList = sorted(sortedList, key=lambda t:t[2].get(), reverse=True)
		for (rowG,col,nbE) in sortedList:
			if nbE > limit:
				outputStream.write('<tr><th>\n')
				outputStream.write(rowG.toSVG(100,arrow))
				outputStream.write( 'Total err = '+str(nbE)+'</th>')
				arrow = False
				for (g,v) in col.getIter():
					if v.get() > limit:
						outputStream.write('<td>')
						outputStream.write(g.toSVG(100,arrow))
                                                viewStr = ""
                                                if(len(v.getList())> 0):
                                                        viewStr = '<a href="' + (",").join(v.getList())+'"> View </a>'
						outputStream.write('<h2>'+str(v) + '</h2>'+viewStr+'</td>')
					else:
						hiddenErr = hiddenErr + v
				outputStream.write('</tr>\n')
			else:
				hiddenErr = hiddenErr + nbE
                outputStream.write('</table><p> Total hidden errors : ')
                viewStr = ""
                if(len(hiddenErr.getList())> 0):
                        viewStr = '<a href="' + (",").join(hiddenErr.getList())+'"> View </a>'
		outputStream.write(str(hiddenErr) + viewStr + '</p>')
                return hiddenErr
		
		
class ConfMatrixObject(object):
	
	def __init__(self,*args):
		self.mat = SmDict()
	
	def incr(self, obj, row, column,elem=None):
		self.mat.get(obj, ConfMatrix).incr(row, column,elem)

	def __str__(self):
		return str(self.mat)


	def toHTML(self, outputStream, limit = 0,viewerURL=""):
                """ write in the output stream the HTML code for this matrix and
                use the ConfMatrix.toHTML to write the submatrices.
                The list of files with error is prefixed with the param viewerURL
                in the href attribute. """
                outputStream.write(' <table border="2"><tr>')
		arrow = True
		hiddenErr = Counter()
		sortedList = []
                # first count all errors for each object (over the full sub matrix)
		for (obj,errmat) in self.mat.getIter():
			nbE = Counter()
                        for (_,c) in errmat.mat.getIter():
                                nbE = nbE + sum([v for (_,v) in c.getIter()], Counter())
			sortedList.append((obj,errmat,nbE))
		sortedList = sorted(sortedList, key=lambda t:t[2].get(), reverse=True)

		for (obj,errmat,nbE) in sortedList:
			if nbE > limit:
				outputStream.write('<tr><th>\n')
				outputStream.write(obj.toSVG(200,arrow))
				outputStream.write( 'Total err = '+str(nbE)+'</th><td>')
				arrow = False
				hiddenErr = hiddenErr + errmat.toHTML(outputStream,limit, viewerURL)
				outputStream.write('</td></tr>\n')
			else:
				hiddenErr = hiddenErr + nbE
		outputStream.write('</table><p> Total hidden errors : ')
                viewStr = ""
                if(len(hiddenErr.getList())> 0):
                        viewStr = '<a href="' + viewerURL+ (",").join(hiddenErr.getList())+'"> View </a>'
		outputStream.write(str(hiddenErr) + viewStr + '</p>')
		
	
