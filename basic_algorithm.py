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


def classes_to_test_out_of(graph, cycles):
    class_cycle_count = {node: 0 for node in graph.nodes()}

    for cycle in cycles:
        for node in cycle:
            class_cycle_count[node] += 1

    max_cycles = max(class_cycle_count.values())
    classes_to_test = [node for node, count in class_cycle_count.items() if count == max_cycles]

    return classes_to_test


if __name__ == "__main__":
    filename = "sample.txt"
    num_nodes, graph = read_input_file(filename)

    removed_nodes = []
    test_out = list(nx.simple_cycles(graph))
    classes_to_test = []
    while len(test_out) > 0:

        # Determine classes to test out of
        classes_to_test = classes_to_test_out_of(graph, test_out)

        # Remove first node in list
        node_to_remove = classes_to_test[0]
        removed_nodes.append(node_to_remove)
        graph.remove_node(node_to_remove)

        # see how many cycles are left now
        test_out = list(nx.simple_cycles(graph))

    with open("output.txt", 'w') as f:
        f.write(f"{len(removed_nodes)}\n")
        f.write(" ".join(map(str, removed_nodes)))

    print(len(removed_nodes))
    print(removed_nodes)
