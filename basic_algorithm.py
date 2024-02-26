import networkx as nx


def read_input_file(filename):
    with open(filename, 'r') as f:
        num_nodes = int(f.readline().strip())
        graph = nx.DiGraph()

        for i in range(num_nodes):
            line = f.readline().strip().split()
            node = int(line[0])
            neighbors = map(int, line[1:])
            graph.add_edges_from([(neighbor, node) for neighbor in neighbors])

        return num_nodes, graph


def find_cycles(graph):
    cycles = list(nx.simple_cycles(graph))
    return cycles


def classes_to_test_out_of(graph, cycles):
    class_cycle_count = {node: 0 for node in graph.nodes()}

    for cycle in cycles:
        for node in cycle:
            class_cycle_count[node] += 1

    max_cycles = max(class_cycle_count.values())
    classes_to_test = [node for node, count in class_cycle_count.items() if count == max_cycles]

    return classes_to_test


def remove_node_and_reevaluate(graph, node):
    # Remove the node and its edges
    graph.remove_node(node)
    # Reevaluate cycles in the updated graph
    cycles = find_cycles(graph)
    # Determine classes to test out of
    classes_to_test = classes_to_test_out_of(graph, cycles)
    return classes_to_test

if __name__ == "__main__":
    filename = "graph.txt" 
    num_nodes, graph = read_input_file(filename)

    removed_nodes = []

    while True:
        # Find cycles in the graph
        cycles = find_cycles(graph)
        if not cycles:
            print(len(removed_nodes))
            print(" ".join(map(str, removed_nodes)))
            break

        # Determine classes to test out of
        classes_to_test = classes_to_test_out_of(graph, cycles)

        # Remove a node (for example, the first node in the list)
        node_to_remove = classes_to_test[0]
        removed_nodes.append(node_to_remove)
        remove_node_and_reevaluate(graph, node_to_remove)
