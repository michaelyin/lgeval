################################################################
# evallg.py
#
# Program that reads in two .lg (CSV) files, computes metrics,
# and returns the result as a (CSV) entry, along with a
# CSV entry (row) for each specific error on standard output.
#
# *If run in 'batch' mode, a CSV file for errors and a separate
# file containing all errors observed will be produced.
#
# Author: R. Zanibbi, June 2012
# Copyright (c) 2012, Richard Zanibbi and Harold Mouchere
################################################################
import sys
import csv
from lg import *
from lgio import *

def runBatch(fileName, defaultFileOrder):
	"""Compile metrics for pairs of files provided in a CSV
	file. Store metrics and errors in separate files."""
	fileReader = csv.reader(open(fileName))
	metricStream = open(fileName + '.m','w')
	diffStream = open(fileName + '.diff','w')

	for row in fileReader:
		# Skip comments and empty lines.
		if not row == [] and not row[0].strip()[0] == "#":
			lgfile1 = row[0].strip() # remove leading/trailing whitespace
			lgfile2 = row[1].strip()
			if not defaultFileOrder:
				temp = lgfile2
				lgfile2 = lgfile1
				lgfile1 = temp
			print ("Test: "+lgfile1+" vs. "+lgfile2);
			# Here lg1 is the output, and lg2 the ground truth.
			lg1 = Lg(lgfile1)
			lg2 = Lg(lgfile2)
			out = lg1.compare(lg2)

			metricStream.write('*M,' + lgfile1 + ',' + lgfile2 + '\n')
			writeMetrics(out, metricStream)
			diffStream.write('DIFF,' + lgfile1 + ',' + lgfile2 + '\n')
			writeDiff(out[1], out[3], out[2], diffStream)

	metricStream.close()
	diffStream.close()
		
def main():
	if len(sys.argv) < 3:
		print("Usage: [[python]] evallg.py <file1.lg> <file2.lg> [diff/*]")
		print("   OR  [[python]] evallg.py [batch] <filepair_list> [GT-FIRST]")
		print("")
		print("    For the first usage, return error metrics and differences")
		print("    for  label graphs in file1.lg and file2.lg.")
		print("    A third argument will return just differences ('diff')")
		print("    or just metrics (any other string).")
		print("")
		print("    For the second usage, a file is provided containing pairs of")
		print("    label graph files, one per line (e.g. 'file1, GTruth').")
		print("    A CSV file containing metrics for all comparisons is written")
		print("    to \"filepair_list.m\", and differences are written to a file")
		print("    \"filepair_list.diff\". By default ground truth is listed")
		print("    second on each line of the batch file; any third argument")
		print("    will result in the first element of each line being treated")
		print("    as ground truth - this does not affect metrics (.m), but does")
		print("    affect difference (.diff) output.")
		sys.exit(0)

	showErrors = True
	showMetrics = True

	if sys.argv[1] == "batch":
		# If requested, swap arguments.
		defaultFileOrder = True
		if len(sys.argv) > 3:
			print(">> Treating 1st column as ground truth.")
			defaultFileOrder = False
		runBatch(sys.argv[2], defaultFileOrder)

	else:
		# Running for a pair of files: require default order of arguments.
		if len(sys.argv) > 3:
			if sys.argv[3] == 'diff':
				showMetrics = False
			else:
				showErrors = False
		fileName1 = sys.argv[1]
		fileName2 = sys.argv[2]
		n1 = Lg(fileName1)
		n2 = Lg(fileName2)
		out = n1.compare(n2)

		if showMetrics:
			writeMetrics(out, sys.stdout)
		if showErrors:
			writeDiff(out[1],out[3],out[2], sys.stdout)

main()

