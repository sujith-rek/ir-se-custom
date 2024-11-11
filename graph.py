import networkx as nx
import matplotlib.pyplot as plt
import json
from urllib.parse import urlparse


# Helper function to extract the domain from a URL
def extract_domain(url):
    return urlparse(url).netloc


# Load JSON data
with open("search_results_crawled.json", "r") as file:
    data = json.load(file)[0]  # Assuming the first element in the list is the relevant dictionary

# Initialize graph data structure for domain names only
gr = {}

# Populate the graph dictionary by filtering for cross-domain links
for url, details in data.items():
    # Extract domain name for the current URL
    parent_domain = extract_domain(url)

    # Initialize domain in graph dictionary if not already present
    if parent_domain not in gr:
        gr[parent_domain] = set()

    # Process each link in the sub_links list
    for link in details["sub_links"]:
        child_domain = extract_domain(link)

        # Only add if it's a cross-domain link and not self-referencing
        if child_domain and parent_domain != child_domain:
            gr[parent_domain].add(child_domain)

# Initialize a directed graph in NetworkX
G = nx.DiGraph()

# Add nodes and edges from the graph dictionary
for parent_domain, child_domains in gr.items():
    for child_domain in child_domains:
        G.add_edge(parent_domain, child_domain)

# Plot the graph
plt.figure(figsize=(15, 15))

# Define layout for the nodes
pos = nx.spring_layout(G, seed=42)

# Draw nodes, coloring by domain
node_colors = [hash(domain) % 10 for domain in G.nodes()]  # Simple hash to assign colors by domain
nx.draw_networkx_nodes(G, pos, node_size=50, node_color=node_colors, cmap=plt.cm.tab10)

# Draw edges with directed arrows
nx.draw_networkx_edges(G, pos, edge_color='b', arrows=True, arrowstyle='->', arrowsize=10)

# Draw labels (domain names) for each node
nx.draw_networkx_labels(G, pos, font_size=8)

# Hide axis
plt.axis("off")

# Show the graph
plt.show()
