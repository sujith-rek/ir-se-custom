import networkx as nx
import matplotlib.pyplot as plt
import json
import tldextract
import numpy as np


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

    def get_node_labels(self) -> list:
        """Return the list of node labels (domains) in order."""
        return list(self.G.nodes())

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

    def return_graph_matrix(self) -> np.ndarray:
        """Return the adjacency matrix of the graph."""
        return np.array(nx.adjacency_matrix(self.G).todense().tolist())

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


class PageRank:

    def __init__(self, graph_matrix: np.ndarray, node_labels: list, epsilon: float = 0.85, max_iterations: int = 100,
                 tol: float = 1e-6) -> None:
        self.graph_matrix = np.array(graph_matrix)
        self.node_labels = node_labels  # List of domain names
        self.epsilon = epsilon
        self.max_iterations = max_iterations
        self.tol = tol
        self.page_rank_scores = None

    def normalize_matrix(self) -> np.ndarray:
        num_nodes = self.graph_matrix.shape[0]

        # Normalize columns to sum to 1
        column_sums = self.graph_matrix.sum(axis=0)
        column_sums[column_sums == 0] = 1  # Avoid division by zero for dangling nodes
        normalized_matrix = self.graph_matrix / column_sums

        # Apply damping factor and teleportation
        teleportation_matrix = np.full_like(normalized_matrix, 1 / num_nodes)
        return (1 - self.epsilon) * normalized_matrix + self.epsilon * teleportation_matrix

    def calculate_pagerank(self) -> np.ndarray:
        num_nodes = len(self.graph_matrix)
        rank_scores = np.full(num_nodes, 1 / num_nodes)  # Initial uniform rank scores
        matrix = self.normalize_matrix()

        for _ in range(self.max_iterations):
            new_rank_scores = np.dot(matrix, rank_scores)
            if np.allclose(new_rank_scores, rank_scores, atol=self.tol):
                break
            rank_scores = new_rank_scores

        return rank_scores

    def get_pagerank(self) -> dict:
        self.page_rank_scores = self.calculate_pagerank()
        # Create a dictionary mapping nodes to their scores
        return {self.node_labels[i]: self.page_rank_scores[i] for i in range(len(self.node_labels))}

    def get_max_pagerank(self) -> str:
        max_index = np.argmax(self.page_rank_scores)
        max_score = np.max(self.page_rank_scores)
        max_node = self.node_labels[max_index]
        return f"Node '{max_node}' has the highest PageRank score of {max_score:.6f}"

    def display_pagerank(self) -> list:
        pagerank_scores = self.get_pagerank()
        sorted_scores = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)

        print("\nPageRank Scores:")
        for node, score in sorted_scores:
            print(f"Node: {node}, Score: {score:.6f}")

        return sorted_scores
