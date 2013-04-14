################################################################
# sumDiff.py
#
# Program that reads in a .diff (CSV) file containing differences between
# to BG, and outputs confusion matrix for symbols and spatial relations.
# Output is in CSV or HTML formats.
# 
# Author: H. Mouchere, June 2012
# Copyright (c) 2012, Richard Zanibbi and Harold Mouchere
################################################################
import sys
import csv
import collections

def addOneError(confM, id1, id2):
	#thanks to "defaultdict" there is nothing to do !
	confM[id1][id2] += 1

def affMat(output, allID, confM):
	output.write(" ")
	for k in sorted(allID):
		output.write(",'"+str(k)+"'")
	output.write("\n")
	for k1 in sorted(allID):
		output.write("'"+str(k1)+"'")
		for k2 in sorted(allID):
			output.write(","+str(confM[k1][k2]))
		output.write("\n")

def affMatHTML(output, allID, confM):
	output.write("<table>\n<tr><th></th>")
	for k in sorted(allID):
		output.write("<th>"+str(k)+"</th>")
	output.write("</tr>\n")
	for k1 in sorted(allID):
		output.write("<tr><th>"+str(k1)+"</th>")
		i = 0
		for k2 in sorted(allID):
			val = str(confM[k1][k2])
			if val == "0":
				val = ""
			output.write('<td class="col_'+str(i)+'">'+val+"</td>")
			i = i+1
		output.write("<th>"+str(k1)+"</th></tr>\n")
	output.write("<tr><th></th>")
	for k in sorted(allID):
		output.write("<th>"+str(k)+"</th>")
	output.write("</tr>\n")		
	output.write("</table>\n")

def writeCSS(output, allID):
	output.write('<head><style type="text/css">\n')
	output.write('table{border-collapse:collapse;}\n')
	output.write('table, td{border: 1px solid lightgray;}\n')
	output.write('th{border: 2px solid black;}\n')
	output.write('h2 {	color: red;}\n')
	output.write('tr:hover{background-color:rgb(100,100,255);}\n ')
	#i = 0
	#for k1 in sorted(allID):
	#	output.write('td.col_'+str(i)+':hover {\nbackground-color:rgb(100,100,255);\n}\n')
	#	i = i+1
	output.write('td:hover{background-color:yellow;} \n')
	output.write('</style></head>\n')

def main():
	if len(sys.argv) < 2:
		print("usage : [[python]] sumDiff.py <file1.diff> [HTML]\n")
		print("	Merge results for each line in a confusion Matrix.")
		print("	By default output is sent to stdout in CSV format.")
		print("	[HTML] option changes output format to HTML")
		sys.exit(0)
	# Read data from CSV file.
	fileName = sys.argv[1]
	try:
		fileReader = csv.reader(open(fileName))
	except:
		sys.stderr.write('  !! IO Error (cannot open): ' + fileName)
		sys.exit(0)
	withHTML = False
	if len(sys.argv) > 2:
		withHTML = True
	#confusion matrix = dict->dict->int
	labelM = collections.defaultdict(collections.defaultdict(int).copy)
	spatRelM = collections.defaultdict(collections.defaultdict(int).copy)
	allLabel = set()
	allSR = set()
	rowCount = -1
	for row in fileReader:
		rowCount += 1

		# Skip blank lines.
		if len(row) == 0:
			continue

		entryType = row[0].strip()
		#skip file names
		if entryType == "DIFF":
			continue
		#process node label errors
		elif entryType == "*N":
			addOneError(labelM,row[2].strip(),row[5].strip())
			allLabel.add(row[2].strip())
			allLabel.add(row[5].strip())

		#process link errors
		elif entryType == "*E":
			# DEBUG
			if row[3].strip() == "1.0" or row[6].strip() == "1.0":
				print("ERROR at row: " + str(rowCount) + " for file: " + fileName)
				print(row)
			elif not len(row) == 8:
				print("INVALID LENGTH at row: " + str(rowCount) + " for file: " + fileName)
				print(row)
			addOneError(spatRelM,row[3].strip(),row[6].strip())
			allSR.add(row[3].strip())
			allSR.add(row[6].strip())
		elif entryType == "*S":
			# Currently ignore segmentation errors (i.e. object-level errors)
			continue
		

	if withHTML:
		sys.stdout.write('<html>')
		writeCSS(sys.stdout, allLabel.union(allSR))
		print ("<h1>"+fileName+"</h1>")
		print ("<b>Rows</b>: Output labels <b>Columns</b>: Ground truth labels")
		print ("")
		print ("<h2>Stroke label confusion matrix (errors only)</h2>")
		print ("<p>"+str(len(allLabel)) + " symbol labels</p>")
		affMatHTML(sys.stdout, allLabel, labelM)
		print ("<h2>Spatial Relation confusion matrix (errors only)</h2>")
		print ("<p>"+str(len(allSR)) + " SR labels</p>")
		affMatHTML(sys.stdout, allSR, spatRelM)
		sys.stdout.write('</html>')
	else:
		affMat(sys.stdout, allLabel, labelM)
		affMat(sys.stdout, allSR, spatRelM)
		
main()
