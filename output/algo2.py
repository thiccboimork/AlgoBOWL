#!/usr/bin/env python

import os
import datetime
#import signal
import random
import networkx as nx
import itertools
import functools
import os
import sys

# go to time or 9:20
number = sys.argv[1]
try:
    hour = int(sys.argv[2])
except:
    hour = 21
try:
    minute = int(sys.argv[3])
except:
    minute = 20

go_until = datetime.datetime.now().replace(hour=hour, minute=minute, second=0)

#class wants:
#    notexit = False
#    exit = False
#def get_ctrlC(sig, frame):
#    if not wants.notexit:
#        sys.exit(1)
#    wants.exit = True
#signal.signal(signal.SIGINT, get_ctrlC)

#random.seed(2)

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
            print (Total.t//100, file=sys.stderr)
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
    # remove nrem random nodes and try to put as many back as possible
    def optimize(sub, nrem):
#        wants.notexit = True
#        rems = [t[0] for t in sorted(
#            ((node, len(graph.in_edges(node))+len(graph.out_edges(node)))
#            for node in sub.nodes),
#            key = lambda t: -t[1]
#        )][:nrem]
        makerem = lambda: random.sample(sorted(sub.nodes), min(nrem, len(sub.nodes)))
        sub3 = None
        for i,rem in enumerate(makerem() for _ in range(1)):
            print (f'Optimizing {len(rem)} nodes', file=sys.stderr)
            sub2 = sub.copy()
            for r in rem:
                remove_node(sub2, r)
            adds = [node for node in graph if node not in sub2]
            random.shuffle(adds)
            for add in adds:
                add_node(sub2, add)
#            if sub3 is None or len(sub2) > len(sub3):
#                sub3 = sub2.copy()
            sub3 = sub2
        return sub3
    print ('Adding first round...', file=sys.stderr)
    add_nodes = [*graph.nodes]
    # this is bad for our graph, is it ok for others?
    #random.shuffle(add_nodes)
    for node in add_nodes:
        add_node(sub, node)
#    wants.notexit = True
    print (f'Len is {len(graph)-len(sub)}', file=sys.stderr)
    print ('Optimizing...', file=sys.stderr)
    nunop = 0
    is_timeup = False
    while not is_timeup:
        # if we're failing, try randomizing more (...is this good??)
        # 80 (tested) means we get some improvement but don't take forever
        sub2 = optimize(sub, 80*(nunop//3+1))
        improved_by = len(sub2) - len(sub)
        is_timeup = datetime.datetime.now() > go_until
        if improved_by > 0:
            sub = sub2
            print (f'Improved to {len(graph)-len(sub)}', file=sys.stderr)
            nunop = 0
#            if wants.exit:
#                break
        else:
            nunop += 1
            if nunop >= 21:
                print ('Giving up improving', file=sys.stderr)
                break
    #print (len(sub), file=sys.stderr)
#    wants.notexit = False
    return sub

#paths = (os.path.join('inputs', p) for p in os.listdir('inputs'))
paths = [f'inputs/input_group{number}.txt']
pathout = 'inputs/output_group{number}.txt'
for path in sorted(paths):
    graph = read_graph(path)
#    graph = nx.complete_graph(20, nx.DiGraph)
#    graph = nx.cycle_graph(20, nx.DiGraph)
    sub = build_sub(graph)
    removed = [node for node in graph.nodes if node not in sub.nodes]
    graph.remove_nodes_from(removed)
    assert nx.is_directed_acyclic_graph(graph)
    print (f'Graph OK, writing to {pathout}', file=sys.stderr)
    with open(pathout, 'w') as f:
        f.write(
            str(len(removed)) + '\n' +
            ' '.join(map(str, removed))
        )
    print (f'Uploading', file=sys.stderr)
    os.system(f'../algobowl group output --to-group-id {number} upload {pathout}')
