import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd


def print_data(input_data):
    print("Infrastructure Data:")
    print("")
    display_node_table(input_data)
    print("")
    display_function_table(input_data)
    print("")
    display_tables_table(input_data)
    print("")

    print("Monitored Data:")
    print("\n(Workload, Cores)")
    display_function_node_matrix(input_data)
    print("\n(Read,Write)")
    display_function_table_matrix(input_data)
    print("\nTable location")
    display_table_node_matrix(input_data)

def create_graph_from_data(data):
    # Extract node names and their attributes from the data
    node_names = data["node_names"]
    node_cores = data["node_cores"]
    node_memories = data["node_memories"]
    node_storage = data["node_storage"]

    # Create a graph
    G = nx.Graph()

    # Add nodes with their attributes
    for i, node in enumerate(node_names):
        G.add_node(node, cores=node_cores[i], memory=node_memories[i], storage=node_storage[i])

    return G


def add_delay_labels(data, G):
    node_delay_matrix = data["node_delay_matrix"]
    # Add normal edges to the black graph with weights (delays)
    for i, node1 in enumerate(G.nodes):
        for j, node2 in enumerate(G.nodes):
            if i > j:
                weight = node_delay_matrix[i][j]
                G.add_edge(node1, node2, weight=weight, color='black')

    return G


def display_node_table(data):
    node_data = {
        "Node": data["node_names"],
        "Cores": data["node_cores"],
        "Memory (B)": data["node_memories"],
        "Storage (B)": data["node_storage"]
    }
    df = pd.DataFrame(node_data)
    print(df)


def display_function_table(data):
    function_data = {
        "Function": data["function_names"],
        "Cores": data["cores_per_req_matrix"],
        "Memory (B)": data["function_memories"],
        "Max Delay (ms)": data["function_max_delays"]

    }
    df = pd.DataFrame(function_data)
    print(df)


def display_function_node_matrix(data):
    function_names = data["function_names"]
    node_names = data["node_names"]
    workload_on_source_matrix = data["workload_on_source_matrix"]
    cores_per_req_matrix = data["cores_per_req_matrix"]

    # Create a DataFrame with function names as rows and node names as columns
    matrix_data = {}
    for i, function in enumerate(function_names):
        row_data = {}
        for j, node in enumerate(node_names):
            workload = workload_on_source_matrix[i][j]
            cores = cores_per_req_matrix[i][j]
            row_data[node] = (workload, cores)
        matrix_data[function] = row_data

    df = pd.DataFrame(matrix_data).T
    print(df)


def display_function_table_matrix(data):
    function_names = data["function_names"]
    table_names = data["table_names"]
    read_per_req_matrix = data["read_per_req_matrix"]
    write_per_req_matrix = data["write_per_req_matrix"]

    # Create a DataFrame with function names as rows and node names as columns
    matrix_data = {}
    for i, function in enumerate(function_names):
        row_data = {}
        for j, table in enumerate(table_names):
            read = read_per_req_matrix[i][j]
            write = write_per_req_matrix[i][j]
            row_data[table] = (read, write)
        matrix_data[function] = row_data

    df = pd.DataFrame(matrix_data).T
    print(df)


def display_table_node_matrix(data):
    table_names = data["table_names"]
    node_names = data["node_names"]
    v_old_matrix = data["v_old_matrix"]

    # DEBUG
    # print("Table names:", table_names)
    # print("Node names:", node_names)
    # print("v_old_matrix dimensions:", len(v_old_matrix), "x", len(v_old_matrix[0]) if len(v_old_matrix) > 0 else 0)
    # print("v_old_matrix:", v_old_matrix)

    # Create a DataFrame with table names as rows and node names as columns
    matrix_data = {}
    for i, node in enumerate(node_names):
        row_data = {}
        for j, table in enumerate(table_names):
            v_old = v_old_matrix[i][j]
            row_data[table] = v_old
        matrix_data[node] = row_data

    df = pd.DataFrame(matrix_data).T
    print(df)


def display_tables_table(data):
    table_data = {
        "Table": data["table_names"],
        "Size (B)": data["table_sizes"],
    }

    df = pd.DataFrame(table_data)
    print(df)


def draw_topology_graph(data, graph):
    G = add_delay_labels(data, graph)

    pos = nx.spring_layout(G)  # positions for all nodes
    edges = G.edges(data=True)

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=700)

    # Draw edges with weights
    nx.draw_networkx_edges(G, pos, edgelist=edges, width=2)

    edge_labels = {(u, v): d['weight'] for u, v, d in edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    # Draw node labels (only names)
    labels = {node: node for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=10)

    # Show the plot
    plt.show()


def draw_migrations_graph(response_data):
    # Extract nodes, node_delay_matrix, and q_ijt_values from the response
    nodes = response_data["nodes"]
    node_delay_matrix = response_data["node_delay_matrix"]
    q_ijt_values = response_data["q_ijt_values"]

    nodes = [f"node_{chr(97 + i)}" for i in range(len(nodes))]

    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes to the graph
    G.add_nodes_from(nodes)

    # Add edges to the graph based on q_ijt_values
    num_nodes = len(nodes)
    NoMigrations = True
    # Add special edges with color blue if q_ijt is 1
    for key, value in q_ijt_values.items():
        if value == 1:
            NoMigrations = False
            # Extract i, j, t from the key
            i, j, t = map(int, key.strip('q[]').split(']['))
            node1 = nodes[i]
            node2 = nodes[j]
            G.add_edge(node1, node2, color='blue', label=f"t:{t}")

            print(f"Table {t} moved: node_{chr(97 + i)} -> node_{chr(97 + j)}")

    if NoMigrations:
        print("\nNo migrations")

    # Get positions for the nodes in the graph
    pos = nx.spring_layout(G)

    # Draw the graph
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=700, font_size=15, font_color='black',
            font_weight='bold', edge_color='gray', arrows=True)

    # Draw edge labels
    edge_labels = {(u, v): d['label'] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    plt.title("Directed Graph with Labeled Edges")
    plt.show()


def draw_function_dep_graph(response_data):
    # Extract nodes, node_delay_matrix, and q_ijt_values from the response
    nodes = response_data["nodes"]
    c_fi_values = response_data["c_fi_values"]
    mu_jt_values = response_data.get("mu_jt_values", {})
    sigma_jt_values = response_data.get("sigma_jt_values")
    y_ftij_values = response_data.get("y_ftij_values")


    # Create a new dictionary for the node labels
    node_labels = {i: f"node_{chr(97 + i)}" for i in range(len(nodes))}
    # Initialize dictionaries for master tables, slaves, and functions
    node_details = {i: {"master_tables": [], "slaves": [], "functions": []} for i in range(len(nodes))}

    # Update the node labels based on the values in c_fi_values
    for key, value in c_fi_values.items():
        if value == 1.0:  # Check if the value is 1.0
            # Extract f and i from the key 'c[f][i]'
            f, i = map(int, key.strip('c[]').split(']['))

            node_details[i]["functions"].append(f)

            '''
            if ": f" in node_labels[i]:
                node_labels[i] += f",f{f}"
            else:
                node_labels[i] += f": f{f}"
            '''

    # Update the node labels based on the values in mu_i_t_values
    for key, value in mu_jt_values.items():
        if value == 1.0:  # Check if the value is 1.0
            # Extract i and t from the key 'mu[i][t]'
            i, t = map(int, key.strip('mu[]').split(']['))

            node_details[i]["master_tables"].append(t)
            '''
            if ": T" in node_labels[i]:
                node_labels[i] += f",T{t}"
            else:
                if ": f" in node_labels[i]:
                    node_labels[i] += f" | T{t}"
                else:
                    node_labels[i] += f": T{t}"
            '''

    # Update the node labels based on the values in mu_i_t
    for key, value in sigma_jt_values.items():
        if value == 1.0:  # Check if the value is 1.0
            # Extract i and t from the key 'mu[i][t]'
            i, t = map(int, key.strip('sigma[]').split(']['))

            node_details[i]["slaves"].append(t)

            '''
            if f"t{t}" not in node_labels[i]:
                node_labels[i] = f"{node_labels[i]}: t{t}"
            else:
                node_labels[i] = f"{node_labels[i]},t{t}"
            '''
    # Create DiGraph
    G = nx.DiGraph()

    # Add nodes to each graph
    for node in nodes:
        G.add_node(node)
    # Add new directed edges with color red based on y_ftij_values
    print("\nDependencies:\n\n")
    for key, value in y_ftij_values.items():
        if value == 1.0:
            # Extract f, t, i, j from the key 'y[f][t][i][j]'
            f, t, i, j = map(int, key.strip('y[]').split(']['))
            G.add_edge(nodes[i], nodes[j], color='red', label=f't: {t} f: {f}')
            print(f"node_{i} ----- f{f},t{t}----->node_{j}")
    print("")

    # Get positions for the nodes in the graph
    pos = nx.spring_layout(G)

    # Draw the graph
    plt.figure(figsize=(12, 8))

    # Draw edges with specified colors
    edges = G.edges()
    colors = [G[u][v]['color'] for u, v in edges]
    nx.draw(G, pos, with_labels=True, labels=node_labels, node_color='skyblue', node_size=700, font_size=15,
            font_color='black', font_weight='bold', edge_color=colors, edge_cmap=plt.cm.Blues, arrows=True)

    # Draw edge labels
    edge_labels = {(u, v): d['label'] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    plt.title("Directed Graph with Labeled Edges")
    plt.show()

    # Prepare and print the table using pandas
    rows = []
    for node, details in node_details.items():
        row = {
            "Node": f"N{node}",
            "Master Tables": ", ".join(map(str, details["master_tables"])),
            "Slaves": ", ".join(map(str, details["slaves"])),
            "Functions": ", ".join(map(str, details["functions"]))
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    print(df)