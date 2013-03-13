################################################################
# lg2dot.py
#
# Convert a CSV graph to bipartite graph and/or
# a tree/forest of trees.
#
# Author: Richard Zanibbi, June 2012
# Copyright (c) 2012, Richard Zanibbi and Harold Mouchere
################################################################
import sys
from lg import *

def bipartiteNodeString(lg, nodeDiffList):
	dotString = "digraph lg {\n\trankdir=LR; ranksep=1.0;\n\tedge[fontsize=10,weight=1]; node[fontsize=13]; graph[ordering=out];\n"
	i = 0
	dotString = dotString + "\n\t/*  NODES (PRIMITIVES) */"
	for primitive in sorted(list(lg.nlabels.keys())):
		dotString = dotString + \
				"\n\tsubgraph cluster" + str(i) + "{" \
				+ "\n\t\trank=" + str(i+1) + "; color=white;\n\t\t"
		Llabel = str(lg.nlabels[primitive])
		Rlabel = Llabel
		color = 'blue'
		diffLabel = False
		for (id,_,RlabelList) in nodeDiffList:
			if id == primitive:
				Rlabel = str(RlabelList)
				color = 'red,penwidth=2.0,fontcolor=red,peripheries=2'
		
		dotString = dotString + 'L' + primitive + " [label=\"" \
				+  Llabel + "\\n" + primitive \
				+  "\", color = blue];\n\t\t"
		dotString = dotString + 'R' + primitive + " [label=\"" \
				+  Rlabel + "\\n" + primitive \
				+  "\", color = " + color + "];\n\t\t"
		dotString = dotString + "L" + primitive + " -> " \
				+ "R" + primitive + " [style=invis, weight=1000]}\n"
		i = i + 1
	return dotString

def lgsegdot(lg, sdiffs):
	"""Produce a .dot string representation of the segmentation graph
	corresponding to a bipartite graph."""
	# Need to generate clusters differently if we want to show primitives in
	# sorted order.
	dotString = "digraph sg {\n\trankdir=LR; ranksep=1.0;\n\tedge[fontsize=10,weight=1]; node[fontsize=13]; graph[ordering=out];\n"
	lstring = "\n\tsubgraph cluster0 {" \
				+ "\n\t\trank=1; color=white;\n\t\t"
	rstring = "\n\tsubgraph cluster1 {" \
				+ "\n\t\trank=2; color=white;\n\t\t"
	cstring = ""

	i = 0
	dotString = dotString + "\n\t/*  NODES (PRIMITIVES) */"
	for primitive in sorted(list(lg.nlabels.keys())):
		lstring = lstring + 'L' + primitive + " [label=\"" \
				+  str(lg.nlabels[primitive]) + "\\n" + primitive \
				+  "\", color = blue];\n\t\t"
		rstring = rstring + 'R' + primitive + " [label=\"" \
				+  str(lg.nlabels[primitive]) + "\\n" + primitive \
				+  "\", color = blue];\n\t\t"
		cstring = cstring + "\tL" + primitive + " -> " \
				+ "\tR" + primitive + " [style=invis, weight=1000];\n"
		i = i + 1
	lstring = lstring + "}\n"
	rstring = rstring + "}\n"
	dotString = dotString + rstring + lstring + cstring

	# Compute segment information. We only need the maps (and diffs,
	# if provided)
	(segmentPrimitiveMap, primitiveSegmentMap, _, _) \
			= lg.segmentGraph()

	dotString = dotString + "\n\t/*  EDGES (COMMON SEGMENTS) */\n"
	for cid in sorted(list(primitiveSegmentMap.keys())):
		csegment = primitiveSegmentMap[cid]
		#print(segmentPrimitiveMap[csegment])
		commonIds = segmentPrimitiveMap[csegment][0] 
		#sorted(list(segmentPrimitiveMap[csegment]))
		for neighbor in commonIds: #[1]:
			if not neighbor == cid:
				color = ""
				if cid in sdiffs.keys():
					errorEdges = sdiffs[cid]
					# Color false positives red.
					if neighbor in errorEdges[0]:
						color = ",color=red,penwidth=3.0"
				dotString = dotString + "\tL" + cid + " -> " + "R" + neighbor \
					+ " [dir=none" + color + "];\n"

		# Show false negative as red dashed lines.
		if cid in sdiffs.keys():
			errorEdges = sdiffs[cid]
			for primitive in errorEdges[1]:
				if not primitive == cid:
					dotString = dotString + "\tL" + cid + " -> " + "R" + primitive \
						+ " [dir=none,color=red,penwidth=3.0,style=dashed];\n"

	dotString = dotString + "}"
	return dotString

def lgdot(lg, nodeDiffList, edgeDiffList):
	"""Produce a .dot string representation a bipartite graph. Note that
	associated *node and edge weights are inserted verbatim* - the graph must
	be filtered if one wants a more compact graph."""
	dotString = ""

	dotString = dotString + bipartiteNodeString(lg,nodeDiffList)
	
	# [Doesn't work...] IMPOSE ORDERING ON NODES FOR LEGIBILITY
	#previous = ""
	#for primitive in sorted(list(lg.nlabels.keys())):
	#	if not previous == "":
	#		dotString = dotString + "\tL" + previous + " -> " \
	#			+ "L" + primitive + " [style=invis];\n"
	#		dotString = dotString + "\tR" + previous + " -> " \
	#			+ "R" + primitive + " [style=invis];\n"
	#	previous = primitive

	dotString = dotString + "\n\t/*  EDGES (PRIMITIVE RELATIONSHIPS) */\n"
	edges = lg.elabels.keys()

	# Edges/Mislabeled edges from graph lg, as appropriate.
	for (parent, child) in sorted(list(edges)):
		errorString = ""
		for (pair,_,oelabel) in edgeDiffList:
			# NOTE: specific to current implementation for missing edge repr.
			if pair == (parent,child):
				errorString = ",color=red,penwidth=3.0,fontsize=14,fontcolor=red"
		labelString = str(lg.elabels[(parent,child)])
		dotString = dotString + "\tL" + parent + " -> " + "R" + child \
			+ " [label=\"" + labelString + "\"" \
			+ errorString + "];\n"

	# Check for missing edges.

	for ((parent,child), labels, _) in edgeDiffList:
		if labels == [('_',1.0)]:
			errorString = ",color=red,penwidth=3.0,fontcolor=red"
			dotString = dotString + "\tL" + parent + " -> " + "R" + child \
				+ " [fontsize=14,label=\"M\"" + errorString + "];\n"

	dotString = dotString + "}"
	return(dotString)

def dagSegmentString(lg, lg2, segPrimMap, primSegMap, correctSegs):
	dotString = "digraph dag {\n\trankdir=LR; ranksep=1.0;\n\tedge[fontsize=13,weight=1]; node[fontsize=13]; graph[ordering=out];\n"

	dotString = dotString + "\n\t/*  SEGMENTS  */\n\t"
	for segmentId in sorted(list(segPrimMap.keys())):
		color = 'red,penwidth=2.0,peripheries=2,fontcolor=red'
		BadSegmentation = True

		# Search for this segment in the list of correct segments.
		for (sid, primSet) in correctSegs:
			if segmentId == sid:
				BadSegmentation = False
				color = 'blue'
				break

		segIds = segPrimMap[ segmentId ]
		slabel = segIds[1]

		# DEBUG: then check classification; this is done using node labels.
		if not BadSegmentation and not slabel == lg2.nlabels[ list(segIds[0])[0] ]:
			color = 'red,fontcolor=red,shape=box,peripheries=2'

		dotString = dotString + segmentId + " [label=\"" \
				+  str(slabel) + "\\n" \
				+  segmentId + "\\n"\
				+  str(sorted(list(segIds[0]))) + "\", color = " + color + "];\n\t"
	return dotString

def dagSegmentRelString(lg, segPrimMap, treeEdges, otherEdges, segmentEdges,\
		treeOnly, segRelDiffs ):
	dotString = "\n\t/*    EDGES (SEGMENT RELATIONSHIPS)    */\n\t"

	set(treeEdges)
	for edge in segmentEdges:
		formatting = ""
	
		# Identify edges with errors.
		if edge in segRelDiffs.keys():
			formatting +=",color=red,fontcolor=red,penwidth=3"

		# Identify DAG edges (non-tree) - skip for tree output.
		if edge not in treeEdges:
			formatting += ",style=dotted"
			if treeOnly:
				continue

		# Produce edge labels.
		parentPrim = list(segPrimMap[ edge[0] ][0])[0]
		childPrim = list(segPrimMap[ edge[1] ][0])[0]
		elabel = lg.elabels[ (parentPrim, childPrim) ]

		dotString += str(edge[0]) + ' -> ' + str(edge[1])
		dotString += " [label=\"" + str(elabel) + "\""+ formatting + "]" + ';\n\t'

	dotString += '\n}'
	return dotString
	

def lgDag(lg, lg2, treeOnly, correctSegs, segRelDiffs):
	"""Show bipartite graph as a tree."""
	(segmentPrimitiveMap, primitiveSegmentMap, noparentSegments, segmentEdges) = \
				lg.segmentGraph()
	(rootNodes, treeEdges, otherEdges) = lg.separateTreeEdges()
	head = dagSegmentString(lg,lg2, segmentPrimitiveMap, primitiveSegmentMap,\
			correctSegs)
	rest = dagSegmentRelString(lg, segmentPrimitiveMap, treeEdges, otherEdges,\
			segmentEdges, treeOnly, segRelDiffs)
	return head + rest


def main():
	if len(sys.argv) < 2:
		print("Usage: [[python]] lg2dot.py <lg.csv> [lg2.csv] [s | d | t]")
		print("")
		print("    Produce a dot file showing a bipartite graph (default)")
		print("    or a segmentation graph (\"s\"), relation DAG (\"d\") or")
		print("    relation tree (\"t\"). If two files are provided,")
		print("    both must be comprised of the same primitives/nodes. For")
		print("    two files, disagreements between the first graph and the")
		print("    second are shown in red.")
		print("")
		print("    NOTE: differences for bipartite and segmentation graphs")
		print("    show false negatives and false positives; for relation")
		print("    DAGs and trees, only 'false positives' for the first")
		print("    file are shown.")
		sys.exit(0)

	fileName = sys.argv[1]
	lg = Lg(fileName)

	# Hide unlabeled edges.
	lg.hideUnlabeledEdges()

	if len(sys.argv) == 2:
		# Show the bipartite graph in isolation.
		print( lgdot(lg, [], []) )

	elif len(sys.argv) == 3:
		# Single graphs:
		# - DAG graph over segments (d)
		# - Tree(s) over segments (t)
		# - Segmentation graph (s)
		# OR bipartite primitive graph difference (default)

		# HACK: to get correct segments, compare graph with itself.
		(_, nodeconflicts, edgeconflicts, segDiffs, correctSegs, \
				segRelDiffs) = lg.compare(lg)

		if sys.argv[2] == 'd':
			print(lgDag(lg, lg,  False, correctSegs, segRelDiffs))
		elif sys.argv[2] == 't':
			print(lgDag(lg, lg, True, correctSegs, segRelDiffs))
		elif sys.argv[2] == 's':
			print( lgsegdot(lg, {}) )
		else:
			# Compare two bipartite graphs.
			# Compute graph difference.
			comparisonFileName = sys.argv[2]
			lg2 = Lg(comparisonFileName)
			(_, nodeconflicts, edgeconflicts, segDiffs, correctSegs, \
				segRelDiffs) = lg.compare(lg2)
			print( lgdot(lg, nodeconflicts, edgeconflicts) )

	elif len(sys.argv) > 3:
		# Compute graph difference.
		comparisonFileName = sys.argv[2]
		lg2 = Lg(comparisonFileName)
		(_, nodeconflicts, edgeconflicts, segDiffs, correctSegs, \
			segRelDiffs) = lg.compare(lg2)

		# Show segmentation/DAG/tree if asked.
		if sys.argv[3] == 's':
			print( lgsegdot(lg, segDiffs) )
		elif (sys.argv[3] == 'd'):
			print( lgDag(lg, lg2, False,correctSegs, segRelDiffs) )
		elif (sys.argv[3] == 't'):
			print( lgDag(lg, lg2, True,correctSegs, segRelDiffs) )
		else:
			# Compare two bipartite graphs.
			# Compute graph difference.
			comparisonFileName = sys.argv[2]
			lg2 = Lg(comparisonFileName)
			(_, nodeconflicts, edgeconflicts, segDiffs, correctSegs, \
				segRelDiffs) = lg.compare(lg2)
			print( lgdot(lg, nodeconflicts, edgeconflicts) )

main()

