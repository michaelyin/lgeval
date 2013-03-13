################################################################
# lg.py - Bipartitite Graph Class
#
# Author: R. Zanibbi, June 2012
# Copyright (c) 2012, Richard Zanibbi and Harold Mouchere
################################################################
import csv
import sys
import math
import copy

class Lg(object):
	"""Class for bipartite graphs where the two node sets are identical, and
	multiple node and edge labels are permited. The graph and individual nodes
	and edges have associated values (e.g. weights/probabilities)."""

	# Define graph data elements ('data members' for an object in the class)
	__slots__ = ('file','gweight','nlabels','elabels','error','absentNodes',\
			'absentEdges','hiddenEdges')

	##################################
	# Constructors (in __init__)
	##################################
	def __init__(self,*args): 
		"""Graph data is read from a CSV file or provided node and edge label
		dictionaries.  If invalid entries are found, the error flag is set to
		true, and graph input continues.  In .lg files, blank lines are
		ignored, and # may be used for comment lines in CSV graph files."""
		self.error = False
		self.gweight = 1.0
		self.nlabels = {}
		self.elabels = {}
		self.absentNodes = set([])
		self.absentEdges = set([])
		self.hiddenEdges = {}

		fileName = None
		nodeLabels = {}
		edgeLabels = {}
		if len(args) == 1:
			fileName = args[0]
			self.file = fileName # DEBUG: add filename for debugging purposes.
		else:
			nodeLabels = args[0]
			edgeLabels = args[1]

		if fileName == None:
			# CONSTRUCTOR 1: try to read in node and edge labels.
			self.file = None
			# Automatically convert identifiers and labels to strings if needed.
			for nid in nodeLabels.keys():
				if not isinstance(nid, str):
					nid = str(nid)

				newdict = {}
				for label in nodeLabels[nid].keys():
					if not isinstance(nid, str):
						label = str(label)
					# Weights need to be floats.
					if not isinstance( nodeLabels[nid][label], float ):
						self.error = True
						sys.stderr.write('  !! Invalid weight for node ' + nid + ', label \"' \
								+ label +"\": " + str(nodeLabels[nid][label]) + "\n")
					newdict[ label ] = nodeLabels[nid][label]
				self.nlabels[nid] = newdict

			# WARNING: self-edges are not detected if edge labels used
			# for initialization.
			for eid in edgeLabels.keys():
				if not isinstance(eid[0], str) or not isinstance(eid[1],str):
					eid[0] = str(eid[0])
					eid[1] = str(eid[1])

				newdict = {}
				for label in edgeLabels[eid].keys():
					if not isinstance(label, str):
						label = str(label)
					if not isinstance( edgeLabels[eid][label], float ):
						self.error = True
						sys.stderr.write('  !! Invalid weight for edge ' + str(eid) + ', label \"' \
								+ label +"\": " + str(edgeLabels[eid][label]) + "\n")
					newdict[ label ] = edgeLabels[eid][label]

				self.elabels[eid] = newdict
		else:
			# CONSTRUCTOR 2: Read graph data from CSV file.
			MIN_NODE_ENTRY_LENGTH = 3
			MIN_EDGE_ENTRY_LENGTH = 4
			try:
				fileReader = csv.reader(open(fileName))
			except:
				# Create an empty graph if a file cannot be found.
				# Set the error flag.
				sys.stderr.write('  !! IO Error (cannot open): ' + fileName + '\n')
				self.error = True
				return

			for row in fileReader:
				# Skip blank lines.
				if len(row) == 0 or len(row) == 1 and row[0].strip() == '':
					continue

				entryType = row[0].strip()
				if entryType == 'N':
					if len(row) < MIN_NODE_ENTRY_LENGTH:
						sys.stderr.write(' !! Invalid node entry length: ' \
								'\n\t' + str(row) + '\n')
						self.error = True
					else:
						nid = row[1].strip() # remove leading/trailing whitespace
						if nid in self.nlabels.keys():
							nlabelDict = self.nlabels[ nid ]
							nlabel = row[2].strip()
							if nlabel in nlabelDict:
								# Note possible error.
								sys.stderr.write(' !! Repeated node label entry ('\
										+ self.file + '): ' \
										+ '\n\t' + str(row) + '\n')
								self.error = True
							# Add (or replace) entry for the label.
							nlabelDict[ nlabel ] = float(row[3])
						else:
							# New primitive; create new dictionary for 
							# provided label (row[2]) and value (row[3])
							nid = row[1].strip()
							nlabel = row[2].strip()

							# Feb. 2013 - allow no weight to be provided.
							if len(row) > MIN_NODE_ENTRY_LENGTH:
								self.nlabels[ nid ] = { nlabel : float(row[3]) }
							else:
								self.nlabels[ nid ] = { nlabel : 1.0 }
	
				elif entryType == 'E':
					if len(row) < MIN_EDGE_ENTRY_LENGTH:
						sys.stderr.write(' !! Invalid edge entry length: ' \
								'\n\t' + str(row) + '\n')
						self.error = True
					else:
						primPair = ( row[1].strip(), row[2].strip() )
						if primPair[0] == primPair[1]:
							sys.stderr.write('  !! Invalid self-edge (' +
									self.file + '):\n\t' + str(row) + '\n')
							self.error = True
							nid = primPair[0]
							if nid in self.nlabels.keys():
								nlabelDict = self.nlabels[ nid ]
								nlabel = row[3].strip()
								if nlabel in nlabelDict:
									# Note possible error.
									sys.stderr.write(' !! Repeated node label entry ('\
										+ self.file + '): ' \
										+ '\n\t' + str(row) + '\n')
							# Add (or replace) entry for the label.
							nlabelDict[ nlabel ] = float(row[4])


						elif primPair in self.elabels.keys():
							elabelDict = self.elabels[ primPair ]
							elabel = row[3].strip()
							if elabel in elabelDict:
								# Note possible error.
								sys.stderr.write(' !! Repeated edge label entry (' \
										+ self.file + '):\n\t' + str(row) + '\n')
								self.error = True
							# Add (or replace) entry for the label.
							# Feb. 2013 - allow no weight.
							if len(row) > MIN_EDGE_ENTRY_LENGTH:
								elabelDict[ elabel ] = float(row[4])
							else:
								elabelDict[ elabel ] = 1.0
						else:
							# Add new edge label entry for the new edge label
							# as a dictionary.
							primPair = ( row[1].strip(), row[2].strip() )
							elabel = row[3].strip()
							
							self.elabels[ primPair ] = { elabel : float(row[4]) }

				# DEBUG: complaints about empty lines here...
				elif len(entryType.strip()) > 0 and entryType.strip()[0] == '#':
					# Ignore lines with comments.
					pass
				else:
					sys.stderr.write('  !! Invalid graph entry type (expect N/E): ' \
							+ str(row) + '\n')
					self.error = True
	
		# Add any implicit nodes in edges explicitly to the hash table
		# containing nodes. The 'nolabel' label is '_'.
		anonNode = False
		anodeList = []
		for elabel in self.elabels.keys():
			nid1 = elabel[0]
			nid2 = elabel[1]

			if not nid1 in self.nlabels.keys():
				self.nlabels[ nid1 ] = { '_' : 1.0 }
				anodeList = anodeList + [ nid1 ]
				anonNode = True
			if not nid2 in self.nlabels.keys():
				self.nlabels[ nid2 ] = { '_' : 1.0 }
				anodeList = anodeList + [ nid2 ]
				anonNode = True
		if anonNode:
			sys.stderr.write('  ** Anonymous labels created for:\n\t' \
				+ str(anodeList) + '\n')

	##################################
	# String, CSV output
	##################################
	def __str__(self):
		nlabelcount = 0
		elabelcount = 0
		for nid in self.nlabels.keys():
			nlabelcount = nlabelcount + len(self.nlabels[nid].keys())
		for eid in self.elabels.keys():
			elabelcount = elabelcount + len(self.elabels[eid].keys())

		return 'Nodes: ' + str(len(self.nlabels.keys())) \
				+ ' (labels: ' + str(nlabelcount) \
				+ ')   Edges: ' + str(len(self.elabels.keys())) \
				+ ' (labels: ' + str(elabelcount) \
				+ ')   Error: ' + str(self.error)

	def csv(self):
		"""Construct CSV data file representation as a string."""
		# NOTE: currently the graph value is not being stored...
		nlist = []
		elist = []
		for nkey in self.nlabels.keys():
			nodeLabels = self.nlabels[nkey]
			for nlabel in nodeLabels.keys():
				nstring = 'N,' + nkey + ',' + nlabel + ',' + \
						str(nodeLabels[nlabel]) + '\n'
				nlist = nlist + [ nstring ]

		for npair in self.elabels.keys():
			edgeLabels = self.elabels[npair]
			for elabel in edgeLabels.keys():
				estring = 'E,' + npair[0] + ',' + npair[1] + ',' + elabel + ',' + \
						str(edgeLabels[ elabel ]) + '\n'
				elist = elist + [ estring ]

		# Sort the node and edge strings lexicographically.
		# NOTE: this means that '10' precedes '2' in the sorted ordering
		nlist.sort()
		elist.sort() 
		sstring = ''
		for nstring in nlist:
			sstring = sstring + nstring
		for estring in elist:
			sstring = sstring + estring
		
		return sstring

	##################################
	# Construct segment-based graph
	# for current graph state
	##################################
	def segmentGraph(self):
		"""Return dictionaries from segments to strokes, strokes to segments,
		segments without parents, and edges labeled as segment ('*')."""
		primitiveSegmentMap = {}
		segmentPrimitiveMap = {}
		noparentSegments = []
		segmentEdges = {}  # Edges between detected objects (segments)

		self.hideUnlabeledEdges()

		# Note: a segmentation edge in either direction merges a primitive pair.
		primSets = {}
		for node in self.nlabels.keys():
			primSets[node] = set([node])
		for (n1, n2) in self.elabels.keys():
			if '*' in self.elabels[(n1,n2)].keys():
				primSets[n1] = primSets[n1].union( set([ n2 ]))
				primSets[n2] = primSets[n2].union( set([ n1 ]))

		# NOTE: Segments are currently assigned the label of the first
		# primitive added to the segmentPrimitiveMap. THIS ASSUMES THAT
		# ALL PRIMITIVES IN A SEGMENT ARE IDENTICALLY LABELED.
		i = 0
		segmentList = []
		rootSegments = set([])
		for primitive in primSets.keys():
			alreadySegmented = False
			for j in range(len(segmentList)):
				if primitive in segmentList[j]:
					primitiveSegmentMap[ primitive ] = 'seg' + str(j)
					alreadySegmented = True
					break

			if not alreadySegmented:
				# Add the new segment.
				newSegment = 'seg' + str(i)
				segmentList = segmentList + [ primSets[primitive] ]
				segmentPrimitiveMap[ newSegment ] = ( primSets[primitive], \
						self.nlabels[primitive] )
				primitiveSegmentMap[ primitive ] = newSegment
				rootSegments = rootSegments.union( set([ newSegment ]))
				i += 1

		# Identify 'root' objects/segments (i.e. with no incoming edges),
		# and edges between objects. **We skip segmentation edges.
		segEdges = {}
		for (n1, n2) in self.elabels.keys():
			segment1 = primitiveSegmentMap[n1]
			segment2 = primitiveSegmentMap[n2] 
			if segment2 in rootSegments:
				rootSegments.remove(segment2)

			for label in self.elabels[(n1,n2)].keys():
				if label != '*' and (segment1, segment2) in segmentEdges.keys():
					if label in segmentEdges[ (segment1, segment2) ].keys():
						# Sum weights for repeated labels
						segmentEdges[ (segment1, segment2)][label] += \
								self.elabels[(n1,n2)][label]
					else:
						# Add unaltered weights for new edge labels
						segmentEdges[ (segment1, segment2) ][label] = \
								self.elabels[(n1,n2)][label]
				elif label != '*':
					segmentEdges[ (segment1, segment2) ] = {}
					segmentEdges[ (segment1, segment2) ][label] = \
							self.elabels[(n1,n2)][label]

		self.restoreUnlabeledEdges()

		return (segmentPrimitiveMap, primitiveSegmentMap, list(rootSegments), \
				segmentEdges)


	##################################
	# Metrics and Graph Differences
	##################################
	def compareSegments(self, lg2):
		"""Compute the number of differing segments, and record disagreements.
		The primitives in each graph should be of the same number and names
		(identifiers). Nodes are merged that have identical (label,value)
		pairs on nodes and all incoming and outgoing edges."""
		(sp1, ps1, _, sre1) = self.segmentGraph()
		(sp2, ps2, _, sre2) = lg2.segmentGraph()
		byValue = lambda pair: pair[1]  # define key for sort comparisons.

		allNodes = set(ps1.keys())
		assert allNodes == set(ps2.keys())
	
		edgeDiffCount = 0
		segDiffs = {}
		correctSegments = []
		correctSegmentIds = set([])
		for primitive in ps1.keys():
			# Make sure to skip primitives that were missing ('ABSENT'),
			# as in that case the graphs disagree on all non-identical node
			# pairs for this primitive, and captured in self.absentEdges.
			if not 'ABSENT' in self.nlabels[primitive] and \
					not 'ABSENT' in lg2.nlabels[primitive]:
				# Obtain sets of primitives sharing a segment for the current
				# primitive for both graphs.
				segPrimSet1 = set([])
				segPrimSet2 = set([])

				# Each of sp1/sp2 are a map of ( {prim_set}, label ) pairs.
				segPrimSet1 = sp1[ ps1[primitive] ][0]
				segPrimSet2 = sp2[ ps2[primitive] ][0]

				# Compute differences in node at opposite end.
				diff1 = segPrimSet1.difference(segPrimSet2)
				diff2 = segPrimSet2.difference(segPrimSet1)
				unionDiffs = diff1.union(diff2)
				differingEdges = len(unionDiffs)
				edgeDiffCount = edgeDiffCount + differingEdges

				# Only create an entry where there are disagreements.
				if differingEdges > 0:
					segDiffs[primitive] = ( diff1, diff2 )
				else:
					# Keep track of correct segments.
					if not ps1[primitive] in correctSegmentIds:
						correctSegmentIds.add(ps1[primitive])
						correctSegments = correctSegments + \
							[ (ps1[primitive], segPrimSet1) ]

			# DEBUG: don't record differences for a single node.
			elif 'ABSENT' in self.nlabels[primitive] \
					and len(self.nlabels.keys()) > 1:
				# If node was missing in this graph, treat this graph as having
				# the opposite segmentation relationship of that in the other 
				# graph - in other words, total error, with all pairs incorrect.
				# DEBUG: We are trying to define the opposite of the edges
				# in the other graph in the case of an absent node.
				allOtherNodes = allNodes.difference(set([primitive]))
				ographSegPrimSet = set((sp2[ ps2[primitive] ])[0]).difference(set([primitive]))
				ediff = allOtherNodes.difference(ographSegPrimSet)
				edgeDiffCount = edgeDiffCount + len(ediff) + \
						len(ographSegPrimSet)
				segDiffs[primitive] = ( ediff, ographSegPrimSet )

			# DEBUG: don't record differences for a single node.
			elif len(self.nlabels.keys()) > 1:
				# Similar, for case where node is missing in lg2.
				allOtherNodes = allNodes.difference(set([primitive]))
				graphSegPrimSet = set((sp1[ ps1[primitive] ])[0]).difference(set([primitive]))
				ediff = allOtherNodes.difference(graphSegPrimSet)
				segDiffs[primitive] = ( graphSegPrimSet, ediff )
				edgeDiffCount = edgeDiffCount + len(ediff) + \
						len(graphSegPrimSet)

		# Compute metrics 
		metrics = [ ("SegError", len(sp2.keys()) - len(correctSegments) ) ]
		correctClass = 0
		for (label, primSet) in correctSegments:
			# Get label for the first primtives (all primitives have identical
			# labels in a segment).
			# DEBUG: use only the set of labels, not confidence values.
			if set(self.nlabels[ list(primSet)[0] ].keys()) == \
				set(lg2.nlabels[ list(primSet)[0] ].keys()):
				correctClass += 1
		metrics = metrics + [ ("ClassError", len(sp2.keys()) - correctClass) ] 
		metrics = metrics + [ ("nSeg", len(sp2.keys()) - len(lg2.absentNodes)) ] 
		metrics = metrics + [ ("detectedSeg", len(sp1.keys())) ]

		# Metrics for edges over segments (number and detected...)
		#metrics = metrics + [ ("nSegRelEdges", len(sre2.keys()) - len(lg2.absentEdges)) ]
		metrics = metrics + [ ("dSegRelEdges", len(sre1.keys())) ]

		# Compute the specific 'segment-level' graph edges that disagree, at the
		# level of primitive-pairs. This means that invalid segmentations may
		# still have valid layouts in some cases.
		segRelErrors = 0
		segRelEdgeDiffs = {}
		segRelMatched = set([])

		for thisPair in sre1.keys():
			thisParentIds = set(sp1[ thisPair[0] ][0])
			thisChildIds = set(sp1[thisPair[1] ][0])

			# A 'correct' edge has the same label between all primitives
			# in the two segments.
			error = False
			for parentId in thisParentIds:
				for childId in thisChildIds:
					# DEBUG: compare only label sets, not values.
					if not (parentId, childId) in lg2.elabels.keys() or \
					   not set(self.elabels[ (parentId, childId) ].keys())  == \
							set(lg2.elabels[ (parentId, childId) ].keys()):
						error = True
						segRelErrors += 1
						segRelEdgeDiffs[ thisPair ] = [ ('Error',1.0) ]
						continue

		metrics = metrics + [ ("SegRelError", segRelErrors) ]

		return (edgeDiffCount, segDiffs, correctSegments, metrics, segRelEdgeDiffs)

	def compare(self, lg2):
		"""Returns: 1. a list of (metric,value) pairs,
		2. a list of (n1,n2) node disagreements, 3. (e1,e2) pairs
		for edge disagreements, 4. dictionary from primitives to
		disagreeing segment graph edges for (self, lg2). Node and 
		edge labels are compared using label sets without values, and
		*not* labels sorted by value."""
		metrics  = []
		nodeconflicts = []
		edgeconflicts = []
		byValue = lambda pair: pair[1]  # define key for sort comparisons.

		# FIX number of nodes as number in reference (lg2)
		# For evaluation relative to ground truth, this is more appropriate
		# than the (possibly expanded) number of targets after resolving
		# absent nodes in both directions. Does lead to risk of negative
		# accuracies (more errors than targets).
		numNodes = len(lg2.nlabels.keys())
		(sp2, ps2, _, sre2) = lg2.segmentGraph()
		nSegRelEdges = len(sre2)

		# Handle case of empty graphs, and missing primitives.
		# SIDE EFFECT: 'ABSENT' nodes and edges added to each graph.
		self.matchAbsent(lg2)

		# METRICS
		# Node and edge labels are considered as sets.
		#numNodes = len(self.nlabels.keys())
		nlabelMismatch = 0
		numEdges = numNodes * (numNodes - 1)  # No self-edges.
		numLabels = numNodes + numEdges
		elabelMismatch = 0

		# Mismatched nodes.
		nodeClassError = set()
		for nid in self.nlabels.keys():
			if not set(self.nlabels[nid].keys()) == set(lg2.nlabels[nid].keys()):
				nlabelMismatch = nlabelMismatch + 1
				# Merge labels.
				thisSet = ''.join(sorted(self.nlabels[nid].keys()))
				thatSet = ''.join(sorted(lg2.nlabels[nid].keys()))

				# NOTE: this ignores label confidences - matching only.
				nodeconflicts = nodeconflicts + \
						[ (nid, [ (thisSet, 1.0) ], \
							[(thatSet, 1.0)] ) ]

				#nodeconflicts = nodeconflicts + \
				#		[ (nid, sorted(self.nlabels[nid].items(),key=byValue), \
				#			sorted(lg2.nlabels[nid].items(),key=byValue)) ]
				nodeClassError = nodeClassError.union([nid])

		# Two-sided comparison of *label sets* (look from absent edges in both
		# graphs!) Must check whether edge exists; '_' represents a "NONE"
		# label (no edge).

		# Identify the set of nodes with disagreeing edges.
		# (RZ: Nov. 2012)
		nodeEdgeError = set()
		for (graph,oGraph) in [ (self,lg2), (lg2,self) ]:
			for npair in graph.elabels.keys():
				if not npair in oGraph.elabels.keys() \
						and (not len(graph.elabels[ npair ]) == 1 \
						or not '_' in graph.elabels[ npair ]):
					elabelMismatch = elabelMismatch + 1

					(a,b) = npair
					# Record nodes in invalid edge
					nodeEdgeError = nodeEdgeError.union([a,b])

					# DEBUG: Need to indicate correctly *which* graph has the
					# missing edge; this graph (1st) or the other (listed 2nd).
					if graph == self:
						thisSet = ''.join(sorted(graph.elabels[npair].keys()))
						edgeconflicts = edgeconflicts + \
							[ (npair,[ (thisSet, 1.0) ],\
									[('_', 1.0)]) ]

						#edgeconflicts = edgeconflicts + \
						#	[ (npair, sorted(graph.elabels[npair].items(),\
						#			key=byValue), [('_', 1.0)]) ]
					else:
						thatSet = ''.join(sorted(lg2.elabels[npair].keys()))
						edgeconflicts = edgeconflicts + \
							[ (npair, [('_', 1.0)], \
								[( thatSet, 1.0) ] ) ]
					
	
						#edgeconflicts = edgeconflicts + \
						#	[ (npair, [('_', 1.0)], \
						#		sorted(graph.elabels[npair].items(),\
						#			key=byValue)) ]

		# Obtain number of primitives with an error of any sort.
		nodeError = nodeClassError.union(nodeEdgeError)

		# One-sided comparison for common edges. Compared by 
		# label *sets* for edges in each graph.
		for npair in self.elabels.keys():
			if npair in lg2.elabels.keys() and \
					not set(self.elabels[npair].keys()) == \
						set(lg2.elabels[npair].keys()):
				elabelMismatch = elabelMismatch + 1
				(a,b) = npair

				thisSet = ''.join(sorted(self.elabels[npair].keys()))
				thatSet = ''.join(sorted(lg2.elabels[npair].keys()))
				edgeconflicts = edgeconflicts + \
					[ (npair, [ (thisSet, 1.0) ], \
						[ (thatSet, 1.0) ] ) ]

				#edgeconflicts = edgeconflicts + \
				#	[ (npair, sorted(self.elabels[npair].items(),key=byValue), \
				#		sorted(lg2.elabels[npair].items(),key=byValue)) ]

		# Now compute segmentation differences.
		(segMismatch, segDiffs, correctSegs, scMetrics, segRelDiffs) \
				= self.compareSegments(lg2)

		# UNDIRECTED/NODE PAIR METRICS
		# Compute number of invalid nodePairs
		badPairs = {}
		for ((n1, n2), _, _) in edgeconflicts:
			if not (n2, n1) in badPairs:
				badPairs[(n1, n2)] = True
		incorrectPairs = len(badPairs)

		# Compute number of mis-segmented node pairs.
		badSegPairs = {}
		for node in segDiffs.keys():
			for other in segDiffs[node][0]:
				if not (other, node) in badSegPairs:
					badSegPairs[(node, other)] = True
			for other in segDiffs[node][1]:
				if not (other, node) in badSegPairs:
					badSegPairs[(node, other)] = True
		segPairErrors = len(badSegPairs)

		# Compute performance metrics; avoid divisions by 0.
		cerror = ("D_C", nlabelMismatch) 
		cnerror = ("D_C(%)",0.0)
		if numNodes > 0:
			cnerror = ("D_C(%)", float(nlabelMismatch) / numNodes)
		rerror = ("D_L", elabelMismatch) 
		rnerror = ("D_L(%)", 0.0)
		snerror = ("D_S(%)", 0.0)
		if numEdges > 0:
			rnerror = ("D_L(%)", float(elabelMismatch) / numEdges)
			snerror = ("D_S(%)", float(segMismatch) / numEdges)
		serror = ("D_S", segMismatch) 
		aerror = ("D_B", nlabelMismatch + elabelMismatch) 

		anerror = ("D_Bn(%)",0.0)
		if numLabels > 0:
			anerror = ("D_Bn(%)", float(nlabelMismatch + elabelMismatch)/numLabels)

		
		# DEBUG:
		# Delta E BASE CASE: for a single node, which is absent in the other
		# file, set label and segment edge mismatches to 1 (in order
		# to obtain 1.0 as the error metric, i.e. total error).
		if len(self.nlabels.keys()) == 1 and \
				(len(self.absentNodes) > 0 or \
				len(lg2.absentNodes) > 0):
			elabelMismatch = 1
			segMismatch = 1
		
		errorVal = 0.0
		if numEdges > 0:
			errorVal +=  math.sqrt(float(segMismatch) / numEdges) + \
					 math.sqrt(float(elabelMismatch) / numEdges)
		if numNodes > 0:
			errorVal += float(nlabelMismatch) / numNodes
		errorVal = errorVal / 3.0
		eerror  = ("D_E(%)", errorVal)
	
	#eerror = ("D_E(%)", \
	#				(float(nlabelMismatch) /  numNodes +
	#				 math.sqrt(float(segMismatch) / numEdges) +
	#				 math.sqrt(float(elabelMismatch) / numEdges)) / 3.0)

		# Compile metrics
		metrics = metrics + [ cerror,  serror, rerror, anerror,\
				eerror, cnerror, snerror, rnerror, aerror, \
				("nNodes",numNodes), ("nEdges", numEdges), \
				("nSegRelEdges", nSegRelEdges), \
				("dPairs",incorrectPairs),("segPairErrors",segPairErrors),
				("nodeCorrect", numNodes - len(nodeError))]
		metrics = metrics + scMetrics

		return (metrics, nodeconflicts, edgeconflicts, segDiffs, correctSegs,\
				segRelDiffs)
		
	##################################
	# Manipulation/'Mutation'
	##################################
	def separateTreeEdges(self):
		"""Return a list of root nodes, and two lists of edges corresponding to 
		tree/forest edges, and the remaining edges."""

		# First, obtain segments; perform extraction on edges over segments.
		(segmentPrimitiveMap, primitiveSegmentMap, noparentSegments, \
				segmentEdges) = self.segmentGraph()

		# Collect parents and children for each node; identify root nodes.
		# (NOTE: root nodes provided already as noparentSegments)
		nodeParentMap = {}
		nodeChildMap = {}
		rootNodes = set(segmentPrimitiveMap.keys())
		for (parent, child) in segmentEdges:
			if not child in nodeParentMap.keys():
				nodeParentMap[ child ] = [ parent ]
				rootNodes.remove( child )
			else:
				nodeParentMap[ child ] += [ parent ]

			if not parent in nodeChildMap.keys():
				nodeChildMap[ parent ] = [ child ]
			else:
				nodeChildMap[ parent ] += [ child ]

		# Separate non-tree edges, traversing from the root.
		fringe = list(rootNodes)

		# Filter non-tree edges.
		nonTreeEdges = set([])
		while len(fringe) > 0:
			nextNode = fringe.pop(0)

			# Skip leaf nodes.
			if nextNode in nodeChildMap.keys():
				# DEBUG: need to copy the list of children, to avoid
				# missing child nodes as d.structures are updated.
				children = copy.deepcopy(nodeChildMap[ nextNode ])
				for child in children:
					numChildParents = len( nodeParentMap[ child ] )

					# Filter edges to children that have more than
					# one parent (i.e. other than nextNode)
					if numChildParents == 1:
						# Child in the tree found, put on fringe.
						fringe += [ child ]
					else:
						# Shift edge to non-tree status.
						nonTreeEdges.add((nextNode, child))

						nodeChildMap[ nextNode ].remove(child)
						nodeParentMap[ child ].remove(nextNode)

		# Generate the tree edges from remaining child relationships.
		treeEdges = []
		for node in nodeChildMap:
			for child in nodeChildMap[ node ]:
				treeEdges += [ (node, child) ]

		return (list(rootNodes), treeEdges, list(nonTreeEdges))
					
	def removeAbsent(self):
		"""Remove any absent edges from both graphs, and empty the fields
		recording empty objects."""
		for absEdge in self.absentEdges:
			del self.elabels[ absEdge ]

		for absNode in self.absentNodes:
			del self.nlabels[ absNode ]
		
		self.absentNodes = set([])
		self.absentEdges = set([])

	def addAbsent(self, lg2):
		"""Identify edges in other graph but not the current one."""
		selfNodes = set(self.nlabels.keys())
		lg2Nodes = set(lg2.nlabels.keys())
		self.absentNodes = lg2Nodes.difference(selfNodes)

		# WARN about absent nodes/edges; indicate that there is an error.
		if len(self.absentNodes) > 0:
			sys.stderr.write('  !! Inserting ABSENT nodes for:\n      ' \
					+ self.file + ' vs.\n      ' + lg2.file + '\n      ' \
				+ str(sorted(list(self.absentNodes))) + '\n')
			self.error = True

		# Add "absent" nodes.
		for missingNode in self.absentNodes:
			self.nlabels[ missingNode ] = { 'ABSENT': 1.0 }

		# Add edges for absent elements, to every node in 
		# the now-expanded node set.
		for missingNode in self.absentNodes:
			for node in self.nlabels.keys():
				# Do not create self-edges.
				if not missingNode == node:
					self.elabels[ ( missingNode, node) ] = { 'ABSENT' : 1.0 }
					self.absentEdges.add( (missingNode, node) )

	def matchAbsent(self, lg2):
		"""Add all missing primitives and edges between this graph and
		the passed graph. **Modifies both the object and argument graph lg2."""
		self.removeAbsent()
		self.addAbsent(lg2)

		lg2.removeAbsent()
		lg2.addAbsent(self)


	##################################
	# Routines for missing/unlabeled 
	# edges.
	##################################
	# Returns NONE: modifies in-place.
	def labelMissingEdges(self):
		for node1 in self.nlabels.keys():
			for node2 in self.nlabels.keys():
				if not node1 == node2:
					if not (node1, node2) in self.elabels.keys():
						self.elabels[(node1, node2)] = {'_' : 1.0 }

	# Returns NONE: modifies in-place.
	def hideUnlabeledEdges(self):
		"""Move all missing/unlabeled edges to the hiddenEdges field."""
		# Move all edges labeled '_' to the hiddenEdges field.
		for edge in self.elabels.keys():
			if set( self.elabels[ edge ].keys() ) == \
					set( [ '_' ] ):
				self.hiddenEdges[ edge ] = self.elabels[ edge ]
				del self.elabels[ edge ]

	def restoreUnlabeledEdges(self):
		"""Move all edges in the hiddenEdges field back to the set of
		edges for the graph."""
		for edge in self.hiddenEdges.keys():
			self.elabels[ edge ] = self.hiddenEdges[ edge ]
			del self.hiddenEdges[ edge ]

	##################################
	# Merging graphs
	##################################
	# RETURNS None (modifies 'self' in-place.)
	def merge(self, lg2, ncombfn, ecombfn):
		"""New node/edge labels are added from lg2 with common primitives. The
	   value for common node/edge labels updated using ncombfn and
	   ecombfn respectiveley: each function is applied to current values to
	   obtain the new value (i.e. v1' = fn(v1,v2))."""

		# Deal with non-common primitives/nodes.
		# DEBUG: make sure that all absent edges are treated as
		# 'hard' decisions (i.e. label ('_',1.0))
		self.matchAbsent(lg2)
		self.labelMissingEdges()

		# Merge node and edgelabels.
		mergeMaps(self.nlabels, self.gweight, lg2.nlabels, lg2.gweight, \
				ncombfn)
		mergeMaps(self.elabels, self.gweight, lg2.elabels, lg2.gweight,\
				ecombfn)

				
	# RETURNS None: modifies in-place.
	def addWeightedLabelValues(self,lg2):
		"""Merge two graphs, adding the values for each node/edge label."""
		def addValues( v1, w1, v2, w2 ):
			return w1 * v1 + w2 * v2
		self.merge(lg2, addValues, addValues)
	
	# RETURNS None: modifies in-place.
	def selectMaxLabels(self):
		"""Filter for labels with maximum confidence. NOTE: this will
		keep all maximum value labels found in each map, e.g. if two
		classifications have the same likelihood for a node."""
		for object in self.nlabels.keys():
			max = -1.0
			maxPairs = {}
			for (label, value) in self.nlabels[object].items():
				if value > max:
					max = value
					maxPairs = { label : value }
				elif value == max:
					maxPairs[label] = value

			self.nlabels[ object ] = maxPairs

		for edge in self.elabels.keys():
			max = -1.0
			maxPairs = {}
			for (label, value) in self.elabels[edge].items():
				if value > max:
					max = value
					maxPairs = { label : value }
				elif value == max:
					maxPairs[label] = value

			self.elabels[ edge ] = maxPairs
	
	# RETURNS NONE: modifies in-place.
	def invertValues(self):
		"""Substract all node and edge label values from 1.0, to 
		invert the values. Attempting to invert a value outside [0,1] will
		set the error flag on the object."""
		for node in self.nlabels.keys():
			for label in self.nlabels[ node ]:
				currentValue = self.nlabels[ node ][ label ] 
				if currentValue < 0.0 or currentValue > 1.0:
					sys.stderr.write('\n  !! Attempted to invert node: ' \
							+ node + ' label \"' \
							+ label + '\" with value ' + str(currentValue) + '\n')
					self.error = True
				else:
					self.nlabels[ node ][ label ] = 1.0 - currentValue

		for edge in self.elabels.keys():
			for label in self.elabels[ edge ]:
				currentValue = self.elabels[ edge ][ label ]
				if currentValue < 0.0 or currentValue > 1.0:
					sys.stderr.write('\n  !! Attempted to invert edge: ' + \
							str(edge) + ' label \"' \
							+ label + '\" with value ' + str(currentValue) + '\n')
					self.error = True
				else:
					self.elabels[ edge ][ label ] = 1.0 - currentValue


################################################################
# Utility functions
################################################################
def mergeLabelLists(llist1, weight1, llist2, weight2, combfn):
	"""Combine values in two label lists according to the passed combfn
	function, and passed weights for each label list."""
	# Combine values for each label in lg2 already in self.
	allLabels = set(llist1.items())\
			.union(set(llist2.items()))
	# have to test whether labels exist
	# in one or both list.
	for (label, value) in allLabels:
		if label in llist1.keys() and \
				label in llist2.keys():
			llist1[ label ] = \
				combfn( llist1[label], weight1,\
						llist2[label], weight2 )
		elif label in llist2.keys():
			llist1[ label ] = \
				weight2 * llist2[label]
		else:
			llist1[ label ] = \
				weight1 * llist1[label]


def mergeMaps(map1, weight1, map2, weight2, combfn):
	"""Combine values in two maps according to the passed combfn
	function, and passed weights for each map."""
	# Odds are good that there are built-in function for this
	# operation.
	objects1 = map1.keys()
	objects2 = map2.keys()
	allObjects = set(objects1).union(set(objects2))
	for object in allObjects:
		if object in objects1 and object in objects2:
			# Combine values for each label in lg2 already in self.
			mergeLabelLists(map1[object],weight1, map2[object], weight2, combfn )			
		# DEBUG: no relationship ('missing') edges should
		# be taken as certain (value 1.0 * weight) where not explicit.
		elif object in objects2:
			# Use copy to avoid aliasing problems.
			# Use appropriate weight to update value.
			map1[ object ] = copy.deepcopy( map2[ object ] )
			for (label, value) in map1[object].items():
				map1[object][label] = weight2 * value
			map1[object]['_'] = weight1 
		else:
			# Only in current map: weight value appropriately.
			for (label, value) in map1[object].items():
				map1[object][label] = weight1 * value
			map1[object]['_'] = weight2 

