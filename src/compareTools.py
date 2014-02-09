################################################################
# compareTools.py
#
# Defines how nodes and edges are compared.
# Usable by other packages such as smallGraph
#
# Author: H. Mouchere, Oct. 2013
# Copyright (c) 2013, Harold Mouchere
################################################################

def defaultMetric(labelList1, labelList2):
#new way but with 1 label per node
        diff =  set(labelList1) ^ (set(labelList2)) # symetric diff
        if len(diff) == 0:
                return (0,[])
        else:
                ab = diff&set(labelList1)
                ba = diff&set(labelList2)
                return (max(len(ab),len(ba) ),[(":".join(ab),":".join(ba))])
#old way :        return set(labelList1) == set(labelList2)

def defaultMetricXx(labelList1, labelList2):
#new way but with 1 label per node
        syn = {'X':'x','\\times':'x', 'P':'p', 'O':'o','C':'c', '\\prime':'COMMA'}
        def replace(x):
                if x in syn.keys():
                        return syn[x]
                else:
                        return x
        a = map(replace, labelList1)
        b = map(replace, labelList2)
        diff =  set(a) ^ (set(b)) # symetric diff
        if len(diff) == 0:
                return (0,[])
        else:
                ab = diff&set(a)
                ba = diff&set(b)
                return (max(len(ab),len(ba) ),[(":".join(ab),":".join(ba))])
#old way :        return set(labelList1) == set(labelList2)


cmpNodes = defaultMetricXx
cmpEdges = defaultMetric
