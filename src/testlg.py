################################################################
# testlg.py
#
# Test program for label graph class.
#
# Authors: R. Zanibbi, H. Mouchere
#	June, 2012
# Copyright (c) 2012, Richard Zanibbi and Harold Mouchere
################################################################
from lg import *
#from bestBG import *

def loadFiles(testfiles):
	for nextFile in testfiles:
		print('[ FILE: ' + nextFile + ' ]')
		n = Lg(nextFile)
		print(n)
		print(n.csv())

def testInvalidFiles(testfiles):
	print("--TESTING INVALID FILE INPUT")
	loadFiles(testfiles)

def testInput(testfiles):
	print("-- TESTING FILE INPUT")
	loadFiles(testfiles)

def labelComparison(file1,file2):
	print('\n[ Comparing Labels for FILE: ' + file1 + ' and ' + file2 + ' ]')
	n1 = Lg(file1)
	n2 = Lg(file2)
	print('>> ' + file1 + ' vs. ' + file2)
	out1 = n1.compare(n2)
	for el in out1[0]:
		print('  ' + str(el))
	print('  Node diffs: ' + str(out1[1]))
	print('  Edge diffs: ' + str(out1[2]))
	print('  SegEdge diffs: ' + str(out1[3]))
	print('  Correct Segments: ' + str(out1[4]))

	print('>> ' + file2 + ' vs. ' + file1)
	out2 = n2.compare(n1)
	for el in out2[0]:
		print('  ' + str(el))
	print('  Node diffs: ' + str(out2[1]))
	print('  Edge diffs: ' + str(out2[2]))
	print('  SegEdge diffs: ' + str(out2[3]))
	print('  Correct Segments: ' + str(out1[4]))

def testLabelComparisons(compareFiles):
	print('\n--TESTING METRICS AND ERROR LOCALIZATON')
	for next in compareFiles:
		labelComparison(next[0],next[1])

def testEmpty(emptyFiles):
	print('\n--TESTING EMPTY FILES')
	for next in emptyFiles:
		print("* " + next[0] + " vs. " + next[1])
		labelComparison(next[0],next[1])

	print('\n--TEST NON-EXISTENT FILE')
	notAFile = Lg('thisfiledoesnotexist')
	print("\nError flag set for missing file:" + str(notAFile.error))
	print(notAFile)


def testSegments(segFiles):
	print('\n--TESTING SEGMENTATION')
	for file in segFiles:
		print('\n[ Segmentation for FILE: ' + file + ' ]')
		n = Lg(file)
		(segmentPrimitiveMap, primitiveSegmentMap, noparentSegments, segmentEdges) = \
				n.segmentGraph()
		print('  SEGMENTS -> PRIMITIVES:\n\t' + str(segmentPrimitiveMap))
		print('  PRIMITIVES -> SEGMENTS:\n\t' + str(primitiveSegmentMap))
		print('  NON-PARENT SEGMENTS: ' + str(noparentSegments))
		print('  SEGMENT EDGES:\n\t' + str(segmentEdges))

def testTreeEdges(treeFiles):
	print('\n--TESTING TREE EDGE/LAYOUT TREE EXTRACTION')
	for file in treeFiles:
		print('\n[ Tree Edges for FILE: ' + file + ' ]')
		n = Lg(file)
		(rootNodes,tEdges,oEdges) = n.separateTreeEdges()
		print('  ROOT NODES: ' + str(rootNodes))
		print('  TREE EDGES: ' + str(tEdges))
		print('  NON-TREE EDGES:' + str(oEdges))

def testSummingGraphs(mergeFiles):
	print('\n--TESTS FOR ADDING NODE/EDGE LABEL VALUES')
	for ( file1, file2 ) in mergeFiles:
		print('\n[ Merging ' + file1 + ' and ' + file2 + ']')
		lg1 = Lg(file1)
		lg2 = Lg(file2)
		lg1.addWeightedLabelValues(lg2)
		print(lg1)
		print(lg1.csv())

		print('-- with graph weights 0.25 and 0.75')
		lg1 = Lg(file1)
		lg1.gweight = 0.25
		lg2 = Lg(file2)
		lg2.gweight = 0.75
		lg1.addWeightedLabelValues(lg2)
		print(lg1)
		print(lg1.csv())

def testMaxLabel(mergeFiles):
	print('\n--TESTS FOR SELECTING MAX. VALUE LABELS')
	for ( file1, file2 ) in mergeFiles:
		print('\n[ Selecting max labels from combined ' + file1 + \
				' and ' + file2 + ']')
		lg1 = Lg(file1)
		lg2 = Lg(file2)
		lg1.addWeightedLabelValues(lg2)
		lg1.selectMaxLabels()
		print(lg1)
		print(lg1.csv())

		print('-- with graph weights 0.25 and 0.75')
		lg1 = Lg(file1)
		lg1.gweight = 0.25
		lg2 = Lg(file2)
		lg2.gweight = 0.75
		lg1.addWeightedLabelValues(lg2)
		lg1.selectMaxLabels()
		print(lg1)
		print(lg1.csv())

def testGenAllBG(files):
	print('\n--TESTING GENERATION OF K BEST BG')
	for file in files:
		print('\n[ FILE: ' + file + ' ]')
		lg1 = Lg(file)
		blg = BestBG(lg1,5)
		blg.afficheDP()
		for i in range(5):
			print("BG top "+str(i))
			print(blg.getBG(i).csv())
		
	print ("END")
		
def testInvertValues(files):
	print('\n--TESTING INVERTING LABEL VALUES')
	for file in files:
		print('\n[ FILE: ' + file + ' ]')
		lg1 = Lg(file)
		print(lg1)
		print(lg1.csv())

		# Invert values.
		lg1.invertValues()
		print(lg1)
		print(lg1.csv())
		
		# And back to original values.
		lg1.invertValues()
		print(lg1)
		print(lg1.csv())



def main():
	validfiles = [ \
			'tests/infile1', \
			'tests/infile2', \
			'tests/infile3', \
			'tests/infile4', \
			'tests/infile5', \
			'tests/infile10'
		]

	invalidfiles = [ \
			'tests/infile6', \
			'tests/infile7', \
			'tests/infile8', \
			'tests/infile9'
		]

	compareFiles = [ \
			('tests/infile1','tests/infile1a'), \
			('tests/infile4','tests/infile4a'), \
			('tests/infile4','tests/infile4b'), \
			('tests/res_001-equation006.lg','tests/001-equation006.lg')
		]

	segFiles = [ \
			'tests/infile1', \
			'tests/infile4', \
			'tests/infile5', \
			'tests/segment1', \
			'tests/segment2', \
			'tests/segment3', \
			'tests/segment4', \
			'tests/segment5', \
			'tests/segment6'
		]

	compareFilespaper = [ \
			('tests/paperExampleGT','tests/paperExampleErrA'), \
			('tests/paperExampleGT','tests/paperExampleErrB'), \
			('tests/paperExampleGT','tests/paperExampleErrC'), \
			('tests/paperExampleGT','tests/paperExampleErrD')
		]

	compareEmpty = [ \
			('tests/infile1','tests/emptyfile'),
			('tests/infile11','tests/emptyfile'),
			('tests/infile1','tests/infile11'),
			('tests/infile1','tests/infile3'),
			('tests/emptyfile','tests/paperExampleGT'),
		]

	mergeFiles = [ \
			('tests/infile1','tests/infile1'),
			('tests/infile1','tests/infile11'),
			('tests/infile4','tests/infile4a'),
			('tests/infile4','tests/infile4b'),
			('tests/infile1', 'invalidfile')
		]
		
	filesForBestBG = [ \
			'tests/infile4', \
			'tests/infile5', \
			'tests/infile5b'
		]
	# Input file tests.	
	# testInput(validfiles)
	#testInvalidFiles(invalidfiles)

	# Segmentation tests.
	testSegments(segFiles)

	# Comparison tests.
	#testLabelComparisons(compareFiles)
	#testLabelComparisons(compareFilespaper)
	#testEmpty(compareEmpty)

	# Extracting trees (layout trees)
	# testTreeEdges(segFiles)

	# Merging label graphs
	#testSummingGraphs( mergeFiles )
	#testMaxLabel( mergeFiles )
	
	# generate all best BG
	#testGenAllBG(filesForBestBG)

	#testInvertValues( validfiles + [ 'tests/invalidEdgeValue' ] )

main()
