import networkx as nx
import random
import matplotlib.pyplot as plt


def draw_graph(G):
    pos = nx.spring_layout(G)
    edge_labels = {(u, v): d['weight'] for u, v, d in G.edges(data=True)}

    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=500, font_size=15, font_color='black',
            font_weight='bold', edge_color='gray')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    plt.title("Randomly Generated Tree with Edge Weights")
    plt.show()


def random_delays(num_nodes):
    # Generate a random tree
    G = nx.random_tree(num_nodes)

    # Convert the tree to an undirected graph
    G = G.to_undirected()

    # Add additional random edges
    added_edges = 0
    num_edges = len(G.edges())
    max_edges = ((num_nodes * num_nodes) / 2) - (num_nodes / 2)
    additional_edges = random.randint(0, (max_edges - num_edges)//2)
    while added_edges < additional_edges:
        u, v = random.sample(range(num_nodes), 2)
        if not G.has_edge(u, v):
            G.add_edge(u, v)
            added_edges += 1

    for u, v in G.edges():
        G[u][v]['weight'] = random.randint(1, 10)

    matrix = [[[] for _ in range(num_nodes)] for _ in range(num_nodes)]

    for i in range(num_nodes):
        for j in range(i + 1, num_nodes, 1):
            matrix[i][j] = nx.shortest_path_length(G, i, j, weight='weight')
            matrix[j][i] = matrix[i][j]
    for i in range(num_nodes):
        matrix[i][i] = 0

    #draw_graph(G)

    return matrix



