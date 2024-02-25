#!/usr/bin/env python

# AlgoBOWL Input
#
# Caitlin Garcia
#   Logan Gill
#  Nathan Remaly
#
# Attempts to generate a tough input graph
# by generating several smaller graphs of
# various sizes and structures, then combining
# them into a large, disconnected graph

import argparse
import random
import functools, itertools
import networkx as NX

# seed the random generator for reproducability
seed = 0
random.seed(seed)

def show(graph):
    import matplotlib.pyplot as plt
    NX.draw(graph)
    plt.show()

# Convert a NetworkX directed graph
# into a valid input file string
# with a random node order
def create_input(graph):
    n = graph.number_of_nodes()
    # rename the nodes, randomly and in-place, to [1..n]
    nodes = [*graph.nodes]
    random.shuffle(nodes)
    graph = NX.relabel_nodes(graph, {
        node : i+1
        for i, node
        in enumerate(nodes)
    }, copy = True)
    # build each node's the prerequisite list, prepended by its length
    reqs = (
        [len(req)] + req
        for req in (
            [*graph.predecessors(node)]
            for node in range(1, n+1)
        )
    )
    # f-expressions don't support newline literals
    newline = '\n'
    return f'''
{n}
{newline.join(
    ' '.join(map(str, req))
    for req in reqs
)}
    '''.strip()+'\n'

def verify_input(filename, nodes, edges):
    graph = NX.DiGraph()
    with open(filename) as f:
        nodes = int(next(f).strip())
        for i, line in enumerate(f):
            myclass = i+1
            graph.add_node(myclass)
            nums = map(int, line.strip().split(' '))
            num_prereq = next(nums)
            prereqs = list(nums)
            assert num_prereq == len(prereqs)
            graph.add_edges_from((prereq, myclass) for prereq in prereqs)
    assert nodes == graph.number_of_nodes()
    assert edges == graph.number_of_edges()

# get the disjoint union of multiple graphs
def union(graphs):
    return functools.reduce(NX.disjoint_union, graphs)

# the problem for this challenge is effectively
# "provide a minimal set of nodes in a directed graph which,
#  when removed, will break all cycles in the graph".
# after some thought, this means:
#  - removing nodes which are part of 0 cycles is pointless
#  - removing nodes which are part of any set of cycles is pointless,
#    provided there is a node which is part of a superset of those
# so a solving algorithm could look something like
#  - traverse each cycle, accumulating nodes which
#    by the above criteria are candidates for removal
#  - give each candidate a set of the cycles which it would break
#  - find a minimum set of candidates such that the union
#    of their associated sets of cycles is the entire set of cycles
# therefore, we can pack as much complexity into as small a graph
# as we can by starting with a set candidates and the cycles they
# would break, and generating a minimal graph based on that

# just a namespace for various subgraph generators
class Gen:
    # generate from cycle/candidate set.
    # it's not easy to optimize cycle overlap,
    # especially in a directed graph,
    # so a (non-ideal) solution is that all
    # candidates are arranged on a large loop
    # and every cycle goes around that loop
    # in the same direction, touching only
    # the candidates it contains
    def from_cycles(cycles, cands):
        # build the graph
        graph = NX.DiGraph()
        lastp = 0
        for i, cycle in enumerate(cycles):
            newp = i/len(cycles)
            if newp > (lastp + 0.05):
                lastp = int(20 * newp) / 20
                print (f'Generating from cycles: {int(newp*100)}%')
            inds = [i for i in range(cands) if cycle&(1<<i)]
            graph.add_edges_from(zip(inds, inds[1:]+inds[:1]))
        return graph
    # already acyclic
    def edgeless(n):
        graph = NX.DiGraph()
        graph.add_nodes_from(range(n))
        return graph
    # double a graph n times, so it has 2**n times as many nodes
    def double(graph, n):
        for _ in range(n):
            graph = union((graph, graph))
        return graph
    # minimum removal: 1 node
    def cycle(n):
        return NX.cycle_graph(n, NX.DiGraph)
    # minimum removal: n-1 if remove == 0
    # remove takes that many edges away randomly
    def complete(n, remove = 0):
        graph = NX.complete_graph(n, NX.DiGraph)
        # we prefer removing lower-numbered edges so
        # the edge count distribution is more uneven
        rem_ind = lambda: int(n*(random.random()**2))
        for _ in range(remove):
            try:
                graph.remove_edge(rem_ind(), rem_ind())
            except:
                pass # ignore edges already gone
        return graph
    # 2n x 2n toroidal lattice graph in which
    # each grid cell is a cycle in the opposite
    # direction of its neighbors, like a chessboard.
    # minimum removal: n x n
    def chess(n):
        size = 2*n
        graph = NX.DiGraph()
        graph.add_edges_from((
            # connect points toroidally
            ((x, y), ((x+dx)%size, (y+dy)%size))
            # iterate all grid points in the space
            for (x, y) in itertools.product(range(size), repeat = 2)
            # go either left/right or up/down
            for (dx, dy) in (
                ((1, 0), (-1, 0)),
                ((0, 1), (0, -1))
            )[(x+y)%2]
        ))
        return graph
    # cycles of various sizes all with one shared node
    # minimum removal: 1
    def flower(sizes):
        cycles = (Gen.cycle(size) for size in sizes)
        # rename nodes to be unique except for 0
        cycles = (
            NX.relabel_nodes(cycle, {
                node: (node, i) if node else node
                for node in range(cycle.number_of_nodes())
            })
            for i, cycle in enumerate(cycles)
        )
        return functools.reduce(NX.compose, cycles)
    # random graph with node and edge count
    def random(nodes, edges):
        graph = NX.DiGraph()
        graph.add_edges_from(
            (i%nodes+1, random.randint(1,nodes))
            for i in range(edges)
        )
        return graph

# random cycle/candidate set, represented as a list
# of cycle bitsets with 1s for each candidate it includes
def make_cycles(cycles, cands):
    bit_chance = lambda bits, chance: sum(1<<i for i in range(bits) if random.random()<chance)
    # here, every candidate/cycle connection has a 0.4% chance,
    # for cycles of an average length 24 with 6000 candidate nodes
    return [bit_chance(cands, 0.004) for _ in range(cycles)]

# create the cycle/candidate set to generate from
# this will generate 6000 nodes and ??? edges
# (was manually tuned to nearly fill the graph)
cycles, cands = make_cycles(2425, 6000), 6000

# the various subgraphs our result should contain
pattern = [
    # singleton classes
    (Gen.edgeless, 100),
    # can you find that a large
    # cycle only needs 1 removal?
    (Gen.cycle, 500),
    # minimal solution is n-1,
    # strain cycle counting and
    # test high prerequisite count
    # (remove 4000 edges at random so the prereq
    #  count isn't a perfect 199 every time)
    (Gen.complete, 200, 4000),
    # minimal 1/4 must be removed
    (Gen.chess, 16),
    # min removal again 1, test cycle overlap detection
    (Gen.flower, [2,3,4]*10+list(range(5, 40, 5))),
    # meant to compress maximum problem complexity
    # into the given number of nodes
    (Gen.from_cycles, cycles, cands),
    # large number of small graphs to test good traversal
    # 2**8 = 256 copies of each
    (Gen.double, Gen.cycle(3), 8),
    (Gen.double, Gen.complete(3), 8)
]

# overall, this means there are
#  -  100 disconnected nodes,
#  -  400 nodes in one big cycle,
#  -  200 almost-fully connected nodes,
#  - 1024 nodes in a gearlike grid,
#  -  194 nodes in a flower,
#  - 6000 nodes generated from a conceptual description,
#  - 1536 nodes in 256 3-cycles and 256 fully-connected triangles
#  - (546 nodes will be filled in randomly)

# official AlgoBOWL input restrictions
MAX_NODES = 10**4
MAX_EDGES = 10**5

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()
    print (f'Random was seeded with {seed}')
    # generate all graphs and combine
    graphs = (
        pat[0](*pat[1:])
        for pat in pattern
    )
    print ('Generating and combining subgraphs...')
    combined = union(graphs)
    nodes = combined.number_of_nodes()
    edges = combined.number_of_edges()
    print (f'Built a graph with {nodes} nodes and {edges} edges')
    # fill in extra space randomly
    print (f'Filling in randomly...')
    if nodes < MAX_NODES:
        combined = union((combined, Gen.random(MAX_NODES-nodes, MAX_EDGES-edges)))
    # check input restrictions
    nodes = combined.number_of_nodes()
    edges = combined.number_of_edges()
    print (f'Graph now contains {nodes} nodes and {edges} edges')
    assert nodes <= MAX_NODES and edges <= MAX_EDGES
    # write the formatted input to the provided file
    print ('Writing file...')
    with open(args.filename, 'w') as f:
        f.write(create_input(combined))
    print ('Verifying input file...')
    verify_input(args.filename, nodes, edges)
    print ('Done')
if __name__ == '__main__':
    main()
