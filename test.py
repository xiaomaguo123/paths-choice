#_*_coding:utf-8_*_
import sys
import networkx as nx


G = nx.read_graphml("Rouen")
edges = [['279400197','357372282'],['279400197','1310180195'],['6412134114','2003418670']]
for edge in edges:
    start = edge[0]
    end = edge[1]
    paths = list(nx.all_simple_paths(G,start,end,35))
    for path in paths:
        f = open(start + "_to_" + end + ".log", "a+")
        sys.stdout = f
        print path
        f.close()
