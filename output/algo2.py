#!/usr/bin/env python

import random
import networkx as nx
import itertools
import functools
import os
import sys

def read_graph(path):
    graph = nx.DiGraph()
    with open(path, 'r') as f:
        lines = int(next(f))
        for i, line in zip(itertools.count(1), f):
            graph.add_node(i)
            nedge, *edges = map(int, line.split())
            assert nedge == len(edges)
            graph.add_edges_from((edge, i) for edge in edges)
    return graph

flat = lambda a: [c for b in a for c in b]

def build_sub(graph):
    sub = nx.DiGraph()
    class Total:
        pass
    Total.t = 0
    def add_node(sub, node, p=False):
        Total.t += 1
        if not Total.t%100 and p:
            print (Total.t//100)
        sub.add_node(node)
        all_pred = 0
        for pred in graph.predecessors(node):
            if pred in sub:
                all_pred |= sub.nodes[pred]['preds']
        all_into = 0
        for succ in graph.successors(node):
            if succ in sub:
                all_into |= 1<<succ
        if all_pred & all_into:
            sub.remove_node(node)
            return False
        sub.nodes[node]['preds'] = all_pred | (1<<node)
        sub.add_edges_from((a,b) for a,b in graph.in_edges(node) if a in sub.nodes)
        sub.add_edges_from((a,b) for a,b in graph.out_edges(node) if b in sub.nodes)
        children = flat(nx.dfs_successors(sub, node).values())
        for child in children:
            sub.nodes[child]['preds'] |= sub.nodes[node]['preds']
        return True
    def remove_node(sub, node):
        sub.remove_node(node)
    # is suppposed to optimize the answer
    def optimize():
        rem_lens = {}
        rems = [t[0] for t in sorted(
            ((node, len(graph.in_edges(node))+len(graph.out_edges(node)))
            for node in sub.nodes),
            key = lambda t: -t[1]
        )]
        for rem in [rems[:10]]:
            print ('Optimizing without ', rem)
            sub2 = sub.copy()
            adds = [node for node in graph if node not in rem]
            random.shuffle(adds)
            for r in rem:
                remove_node(sub2, r)
            for add in adds:
                add_node(sub2, add)
            print (len(sub2))
    print ('Adding first round...', file=sys.stderr)
    for node in graph:
        add_node(sub, node)
    #print ('Optimizing...')
    #optimize()
    return sub

#paths = (os.path.join('inputs', p) for p in os.listdir('inputs'))
paths = [sys.argv[1]]
for path in sorted(paths):
    graph = read_graph(path)
#    graph = nx.complete_graph(20, nx.DiGraph)
#    graph = nx.cycle_graph(20, nx.DiGraph)
    sub = build_sub(graph)
    removed = [node for node in graph.nodes if node not in sub.nodes]
    print (len(removed))
    print (' '.join(map(str, removed)))
