import networkx as nx
import matplotlib.pyplot as plt
import json
import tldextract


class DomainGraph:
    def __init__(self) -> None:
        self.G = nx.DiGraph()

    def __extract_domain(self, url: str) -> str:
        """Helper function to extract the domain from a URL."""
        extracted = tldextract.extract(url)
        return f"{extracted.domain}.{extracted.suffix}"

    def build_graph(self, data: dict) -> None:
        """Build the directed graph from the provided data."""
        gr = {}

        # Populate the graph dictionary by filtering for cross-domain links
        for url, details in data.items():
            parent_domain = self.__extract_domain(url)

            if parent_domain not in gr:
                gr[parent_domain] = set()

            for link in details.get("sub_links", []):
                child_domain = self.__extract_domain(link)
                if child_domain and parent_domain != child_domain:
                    gr[parent_domain].add(child_domain)

        # Add nodes and edges to the NetworkX graph
        for parent_domain, child_domains in gr.items():
            for child_domain in child_domains:
                self.G.add_edge(parent_domain, child_domain)

    def draw_graph(self) -> None:
        """Draw the graph using matplotlib."""
        plt.figure(figsize=(15, 15))

        pos = nx.spring_layout(self.G, seed=42)
        node_colors = [hash(domain) % 10 for domain in self.G.nodes()]

        # Draw nodes and edges
        nx.draw_networkx_nodes(self.G, pos, node_size=50, node_color=node_colors, cmap=plt.cm.tab10)
        nx.draw_networkx_edges(self.G, pos, edge_color='b', arrows=True, arrowstyle='->', arrowsize=10)

        # Draw labels for each node
        nx.draw_networkx_labels(self.G, pos, font_size=8)

        plt.axis("off")
        plt.show()

    def draw_from_file(self, file_name: str) -> None:
        """Load JSON data from a file and draw the graph."""
        with open(file_name, "r") as file:
            data = json.load(file)[0]  # Assuming the first element in the list is the relevant dictionary
        self.build_graph(data)
        self.draw_graph()

    def draw_from_json(self, json_data: dict) -> None:
        """Draw the graph from directly provided JSON data."""
        self.build_graph(json_data[0])  # Assuming the first element in the list is the relevant dictionary
        self.draw_graph()
