import networkx as nx


def read_input_file(filename):
    with open(filename, 'r') as f:
        num_nodes = int(f.readline().strip())
        graph = nx.DiGraph()

        for i in range(num_nodes):
            line = f.readline().strip().split()
            neighbors = map(int, line[1:])
            graph.add_edges_from([(neighbor, (i + 1)) for neighbor in neighbors])

        return num_nodes, graph


def remove_nodes_and_verify_dag(graph, nodes_to_remove):
    modified_graph = graph.copy()
    for i in nodes_to_remove:
        modified_graph.remove_node(i)

    is_dag = nx.is_directed_acyclic_graph(modified_graph)

    print("Is DAG:", is_dag)
    return is_dag


if __name__ == "__main__":
    # Input parameters
    input_filename = "graph.txt"

    with open("output.txt", 'r') as f:
        num_nodes = int(f.readline().strip())
        nodes_to_remove = f.readline().split()
        nodes_to_remove = [int(i) for i in nodes_to_remove]

    # Read input file
    num_nodes, graph = read_input_file(input_filename)

    # Remove specified nodes and verify if the resulting graph is a DAG
    is_dag_result = remove_nodes_and_verify_dag(graph, nodes_to_remove)

    # Output result
    num_nodes_removed = len(nodes_to_remove)
    if is_dag_result:
        print("The resulting graph is a DAG.")
    else:
        print("The resulting graph is not a DAG.")
