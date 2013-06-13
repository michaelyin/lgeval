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
	Designed to be used in smDict"""
	
	def __init__(self,*args):
		self.value = 0
	def incr(self):
		self.value = self.value +1
	def get(self):
		return self.value
	def set(self,v):
		self.value = int(v)
	def __str__(self):
		return str(self.value)
	def __int__(self):
		return self.value
	
	
	
class ConfMatrix(object):
	
	def __init__(self,*args):
		self.mat = SmDict()
	
	def incr(self, row, column):
		self.mat.get(row, SmDict).get(column,Counter).incr()
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

	def toHTML(self, outputStream, limit = 0):
		outputStream.write(' <table border="1"><tr>')
		arrow = True
		hiddenErr = 0
		sortedList = []
		for (rowG,col) in self.mat.getIter():
			nbE = sum([v.get() for (_,v) in col.getIter()])
			sortedList.append((rowG,col,nbE))
		sortedList = sorted(sortedList, key=itemgetter(2), reverse=True)
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
						outputStream.write('<h2>'+str(v) + '</h2></td>')
					else:
						hiddenErr = hiddenErr + v.get()
				outputStream.write('</tr>\n')
			else:
				hiddenErr = hiddenErr + nbE
		outputStream.write('</table><p> Total hidden errors : ')
		outputStream.write(str(hiddenErr) + '</p>')
		
		

	
