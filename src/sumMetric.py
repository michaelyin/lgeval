################################################################
# sumMetric.py
#
# Program that reads in a .m (CSV) file containing metrics,
# and outputs summary statistics and global performance metrics.
# 
# Author: H. Mouchere and R. Zanibbi, June 2012
# Copyright (c) 2012, Richard Zanibbi and Harold Mouchere
################################################################
import sys
import csv
import math

def meanStdDev( valueList, scale ):
	"""Compute the mean and standard deviation of a *non-empty* list of numbers."""
	numElements = len(valueList)
	if numElements == 0:
		return(None, 0.0)
	
	mean = float(sum(valueList)) / numElements
	variance = 0
	for value in valueList:
		variance += math.pow( value - mean, 2 )
	variance = variance / float(numElements)
	return (scale * mean, scale * math.sqrt(variance))
	
def weightedMeanStdDev( valueList, weights, scale ):
	"""Compute the weighted mean and standard deviation of a *non-empty* list of numbers."""

	numElements = sum(weights)
	if len(valueList) < 1 or numElements == 0:
		return(None, 0.0)

	mean = 0
	for i in range(len(valueList)):
		mean += float(valueList[i]*weights[i])
	mean = mean / numElements
	variance = 0
	for  i in range(len(valueList)):
		variance += math.pow( valueList[i] - mean, 2 )*weights[i]
	variance = variance / float(numElements)
	
	return (scale * mean, scale * math.sqrt(variance))

def reportMeanStdDev(formatWidth, label, valueList, scale ):
	(m,s) = meanStdDev(valueList,scale)
	printTable(formatWidth,[label,m,s])

def reportWMeanStdDev(formatWidth, label, valueList, weights, scale ):
	(m,s) =  weightedMeanStdDev(valueList,weights,scale)
	printTable(formatWidth,[label,m,s])
	#print(label + " (mean, stdev) = " + str(weightedMeanStdDev(valueList,weights,scale)))
	
def reportCoupleCSV(sep,c ):
	(mean,stdev) = c
	sys.stdout.write(sep + str(mean) + "," + str(stdev))

def intMetric( dictionary, label ):
	return str(int(dictionary[label]))

def floatMetric( dictionary, label ):
	return str(dictionary[label])

def printTable( field_width, entries):
	"""Makes it easier to format output for evaluation metrics."""
	cols = len(entries) 
	labelFormat = ''
	for i in range(0,cols):
		extra = ''
		if type(entries[i]) is float:
			labelFormat += '{0[' + str(i) + ']:>{width}.2f' + '}'
		else:
			labelFormat += '{0[' + str(i) + ']:>{width}}'
	print labelFormat.format( entries, width=field_width)
	

def main():
	if len(sys.argv) < 2:
		print("usage : [[python]] sumMetric.py <file1.m> [CSV] \n")
		print("    [CSV] : print all results in one line \n")
		sys.exit(0)
	showCSV = False
	if len(sys.argv) > 2:
		showCSV = True
	# Read data from CSV file.
	fileName = sys.argv[1]
	try:
		fileReader = csv.reader(open(fileName))
	except:
		sys.stderr.write('  !! IO Error (cannot open): ' + fileName)
		sys.exit(0)

	# Compile distributions for all metrics.
	allValues = {}
	nbEM = 0;
	fileList = []
	for row in fileReader:
		# Skip blank lines.
		if len(row) == 0:
			continue

		entryType = row[0].strip()
		if entryType == "*M":
			fileList = fileList + [row[1]]
			continue
		for i in range(0,len(row),2):
			if row[i].strip() not in allValues:
				allValues[row[i].strip()] = []
			allValues[row[i].strip()] = allValues[row[i].strip()] \
					+ [float(row[i+1].strip())]
		nbEM+=1
	
	# Compile and display the sum for each metric.
	allSum = {}
	allZeroCount = {}
	zeroFileList = {}
	for v in allValues.keys():
		allSum[v] = sum(allValues[v])
		#print(str(v) + " = " + str(allSum[v]))
		allZeroCount[v] = 0
		for s in range(len(allValues[v])):
			if allValues[v][s] == 0:
				allZeroCount[v] += 1
				if v in zeroFileList.keys():
					zeroFileList[v] += '\n' + str(s)
				else:
					zeroFileList[v] = str(s)
				#print fileList[s]
		#print ('    Correct expressions: ' + str(nbZ))

	# Report input counts.
	correctExps = int(allZeroCount["D_B"])
	#sys.stderr.write( str( zeroFileList[ "D_B" ] ) )
	correctExps2 = int(allZeroCount["D_E(%)"])
	#sys.stdout.write( str( zeroFileList[ "D_E" ] ) )
	assert correctExps == correctExps2

	nodes = int(allSum["nNodes"])
	dcTotal = int(allSum["D_C"])
	edges = int(allSum["nEdges"])
	dlTotal = int(allSum["D_L"])
	dsTotal = int(allSum["D_S"])
	dbTotal = int(allSum["D_B"])
	duTotal = int(allSum["dPairs"])
	if showCSV:
		print("D_C,D_L,D_S,D_B,D_B(%),var,D_E(%),var,wD_E(%),var")
		sys.stdout.write(intMetric(allSum,"D_C") + "," +intMetric(allSum, "D_L") \
			 + "," + intMetric(allSum, "D_S") + "," + intMetric(allSum, "D_B"))
		reportCoupleCSV(',',meanStdDev(allValues["D_B(%)"],100))
		reportCoupleCSV(',',meanStdDev(allValues["D_E"],100))
		reportCoupleCSV(',',weightedMeanStdDev(allValues["D_E"],allValues["nNodes"],100))
		print("")
	else:
		fieldWidth = 10
		print("-----------------------------------------------------------------------------------")
		print("  PRIMITIVES")
		print("-----------------------------------------------------------------------------------")
		printTable(fieldWidth,['','Rate(%)','Total','Correct','Errors','SegErr','RelErr'])
		print("")
		print("COMPLETE GRAPHS (FILES)")
		printTable(fieldWidth,['Graph',100 * float(correctExps)/nbEM,nbEM,correctExps,nbEM-correctExps])
		print('')

		print("DIRECTED METRICS")
		nodeRate = 100.0
		if nodes > 0:
			nodeRate = 100 * float(nodes-dcTotal)/nodes
		printTable(fieldWidth,['Node', nodeRate, int(allSum["nNodes"]), nodes - dcTotal, dcTotal ])

	
		edgeRate = 100.0
		if edges > 0:
			edgeRate = 100 * float(edges - dlTotal) / edges
		printTable(fieldWidth,['Edge', edgeRate, edges, edges - dlTotal, dlTotal,\
				dsTotal, dlTotal-dsTotal])

		labelRate = 100.0
		if nodes + edges > 0:
			labelRate =  100 *(nodes + edges - dbTotal)/float(nodes + edges)
		printTable(fieldWidth,['Node+Edge', labelRate, nodes + edges, nodes + edges - dbTotal, dbTotal])

	
		print("")
		# REPEATED FOR CONVENIENCE
		print("UNDIRECTED METRICS")
		printTable(fieldWidth,['Node', nodeRate, int(allSum["nNodes"]), nodes - dcTotal, dcTotal ])

		undirNodeRel = 100.0
		if edges > 0:
			undirNodeRel = 100 * (float(edges)/2 - duTotal)/(edges/2)
		printTable(fieldWidth,['EdgePair', undirNodeRel, edges/2, int(edges)/2 - duTotal, duTotal, int(allSum["segPairErrors"]), duTotal - int(allSum["segPairErrors"])])

		nodeAllRate = 100.0
		nodeAllCorrect = 100.0
		nodePairCorrect = 100.0

		correctNodesAndPairs = nodes - dcTotal + float(edges)/2 - duTotal
		pairCount = edges/2 
		if nodes > 0:
			nodeAllCorrect = int(allSum["nodeCorrect"])
			nodeAllRate = 100 * float(nodeAllCorrect)/nodes
			nodePairCorrect = 100 * float(correctNodesAndPairs)/(nodes + pairCount)

		printTable(fieldWidth,['Node+Pair', nodePairCorrect, nodes + pairCount, int(correctNodesAndPairs), int(dcTotal + duTotal) ])


		# NUMBER OF CORRECT NODES
		#print("")
		#print("CORRECTLY LABELED NODES")
		#printTable(fieldWidth,['*Nodes-CL',nodeAllRate,int(allSum["nNodes"]),nodeAllCorrect, nodes - nodeAllCorrect])


		# Compute bipartite graph (BG) metrics.
		print("")
		print("HAMMING DISTANCES (see DRR 2013 paper)")
		printTable(fieldWidth,['','Mean','Stdev'])
		for metric in [
				('D_B',1),
				('D_C', 1),
				('D_L',1),
				('D_S',1),
				('D_Bn(%)',100),
				('D_E(%)',100),
				]:
			reportMeanStdDev(fieldWidth,metric[0],allValues[metric[0]],\
					metric[1])
		reportWMeanStdDev(fieldWidth,'W-D_E(%)',allValues["D_E(%)"],allValues["nNodes"],100)
		
		# Compute segmentation and classification errors.
		numSegments = int(allSum["nSeg"])
		correctSegments = int(numSegments - allSum["SegError"])
		classErrors = int(allSum["ClassError"])
		correctClass = numSegments - int(allSum["ClassError"])
		numSegRelEdges = int(allSum["nSegRelEdges"])
		detectedSegs = int(allSum["detectedSeg"])
		detectedSegRelEdges = int(allSum["dSegRelEdges"])
		correctSegRelEdges = 0
		if detectedSegRelEdges > 0:
			#correctSegRelEdges = numSegRelEdges - int(allSum["SegRelError"])
			correctSegRelEdges = detectedSegRelEdges - int(allSum["SegRelError"])
		segRelRecall = 100.0
		if numSegRelEdges > 0:
			segRelRecall = 100*float(correctSegRelEdges)/numSegRelEdges
		segRelPrecision = 100.0
		if detectedSegRelEdges > 0:
			segRelPrecision = float(100*float(correctSegRelEdges)/detectedSegRelEdges)
		relFalsePositive = 0
		if detectedSegRelEdges > 0:
			relFalsePositive = detectedSegRelEdges - correctSegRelEdges

	
		print("")
		print("-----------------------------------------------------------------------------------")
		print("  OBJECTS")
		print("-----------------------------------------------------------------------------------")

		printTable(fieldWidth,['','Recall(%)','Prec(%)','Total(GT)','Correct','FalseNeg','*Detected','*FalsePos'])
		segRate = 100.0
		segClassRate = 100.0
		if numSegments > 0:
			segRate = 100 * float(correctSegments)/numSegments
			segClassRate = 100*float(correctClass)/numSegments
		segPrec = 100.0
		segClassPrec = 100.0
		if detectedSegs > 0:
			segPrec = 100 * float(correctSegments)/detectedSegs
			segClassPrec = 100*float(correctClass)/detectedSegs

		print("")
		#print("OBJECT AND OBJECT RELATIONSHIP DETECTION")
		printTable(fieldWidth,['Segments', segRate, \
				segPrec,
				numSegments, correctSegments, numSegments - correctSegments,\
						detectedSegs, detectedSegs - correctSegments ])

		
		printTable(fieldWidth,['Seg+Class', segClassRate, \
				segClassPrec, numSegments, correctClass, numSegments - correctClass,\
				detectedSegs, detectedSegs - correctClass])

		printTable(fieldWidth,['Relations',\
				segRelRecall, \
				segRelPrecision, \
				numSegRelEdges,\
				correctSegRelEdges,\
				numSegRelEdges - correctSegRelEdges, \
				intMetric(allSum, "dSegRelEdges"),\
				relFalsePositive])


		#print("")
		#print("CORRECTLY LABELED OBJECTS")
		#printTable(fieldWidth,['','C.Rate(%)','Total','Correct','Error'])

		#classRate = 100.0
		#if correctSegments > 0:
		#	classRate = 100 *float(correctClass)/correctSegments
		#printTable(fieldWidth,['*Segs-CL', classRate, correctSegments, correctClass, correctSegments - correctClass])
		print("")


main()
