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
    modified_graph.remove_nodes_from(nodes_to_remove)
    
    is_dag = nx.is_directed_acyclic_graph(modified_graph)  # Check if the modified graph is a DAG
    
    print("Is DAG:", is_dag)
    return is_dag

def write_output_file(output_filename, num_nodes_removed, nodes_removed):
    with open(output_filename, 'w') as f:
        f.write(f"{num_nodes_removed}\n")
        f.write(" ".join(map(str, nodes_removed)))

if __name__ == "__main__":
    # Input parameters
    input_filename = "graph.txt"
    output_filename = "output.txt"
    nodes_to_remove = [1, 10, 15, 16, 3, 8, 9, 2, 4, 171, 5]  # Specify nodes to remove

    # Read input file
    num_nodes, graph = read_input_file(input_filename)

    # Remove specified nodes and verify if the resulting graph is a DAG
    is_dag_result = remove_nodes_and_verify_dag(graph, nodes_to_remove)

    # Output result
    num_nodes_removed = len(nodes_to_remove)
    if is_dag_result:
        write_output_file(output_filename, num_nodes_removed, nodes_to_remove)
    else:
        print("The resulting graph is not a DAG.")
