import math
from typing import Dict, List


class VectorSpace:
    def __init__(self):
        self.inverted_index = {}
        self.doc_vectors = {}
        self.doc_lengths = {}
        self.total_docs = 0
        self.docs = {}
        self.idf_values = {}  # Added IDF cache

    def set_docs(self, docs: Dict[str, List[str]]) -> None:
        self.docs = docs
        self.total_docs = len(docs)
        self._build_index()
        self._calculate_idfs()  # Calculate IDF values once

    def _calculate_tf(self, term_freq: int) -> float:
        return 1 + math.log10(term_freq) if term_freq > 0 else 0

    def _calculate_idf(self, doc_freq: int) -> float:
        return math.log10(self.total_docs / float(doc_freq)) if doc_freq > 0 else 0

    def _calculate_idfs(self):
        # Calculate IDF values for all terms
        for term in self.inverted_index:
            doc_freq = len(self.inverted_index[term])
            self.idf_values[term] = self._calculate_idf(doc_freq)

    def _calculate_document_length(self, doc_vector: Dict[str, float]) -> float:
        return math.sqrt(sum(weight * weight for weight in doc_vector.values()))

    def _build_index(self) -> None:
        # Build inverted index and document vectors
        for doc_id, (doc_name, tokens) in enumerate(self.docs.items()):
            # Calculate term frequencies
            term_freqs = {}
            for term in tokens:
                term_freqs[term] = term_freqs.get(term, 0) + 1

            # Calculate TF weights and build inverted index
            doc_vector = {}
            for term, freq in term_freqs.items():
                tf_weight = self._calculate_tf(freq)
                doc_vector[term] = tf_weight

                if term not in self.inverted_index:
                    self.inverted_index[term] = {}
                self.inverted_index[term][doc_id] = tf_weight

            # Store document vector
            self.doc_vectors[doc_id] = doc_vector

        # Apply IDF weights and normalize document vectors
        for doc_id, doc_vector in self.doc_vectors.items():
            # Apply IDF weights
            for term in doc_vector:
                doc_freq = len(self.inverted_index[term])
                idf = self._calculate_idf(doc_freq)
                doc_vector[term] *= idf

            # Normalize document vector
            length = self._calculate_document_length(doc_vector)
            if length > 0:
                for term in doc_vector:
                    doc_vector[term] /= length

    def _calculate_cosine_similarity(self, query_vector: Dict[str, float], doc_vector: Dict[str, float]) -> float:
        common_terms = set(query_vector.keys()) & set(doc_vector.keys())
        dot_product = sum(query_vector[term] * doc_vector[term] for term in common_terms)
        return dot_product

    def rank_documents(self, query_tokens: List[str]) -> List[tuple]:
        # Create query vector with TF-IDF weights
        query_freqs = {}
        for term in query_tokens:
            query_freqs[term] = query_freqs.get(term, 0) + 1

        query_vector = {}
        for term, freq in query_freqs.items():
            if term in self.inverted_index:
                tf = self._calculate_tf(freq)
                idf = self.idf_values.get(term, 0)  # Use cached IDF values
                query_vector[term] = tf * idf

        if not query_vector:
            # If no query vector, assign zero similarity to all documents
            return [(doc_name, 0.0) for doc_name in self.docs.keys()]

        # Normalize query vector
        query_length = self._calculate_document_length(query_vector)
        if query_length > 0:
            for term in query_vector:
                query_vector[term] /= query_length

        # Calculate cosine similarity for all documents
        scores = {}
        for doc_id, doc_vector in self.doc_vectors.items():
            similarity = self._calculate_cosine_similarity(query_vector, doc_vector)
            scores[doc_id] = similarity

        # Include zero scores for documents
        for doc_id in range(self.total_docs):
            if doc_id not in scores:
                scores[doc_id] = 0.0

        # Rank documents by similarity
        ranked_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [(list(self.docs.keys())[doc_id], score) for doc_id, score in ranked_docs]

    def search(self, query_tokens: List[str]) -> List[tuple]:
        results = self.rank_documents(query_tokens)
        print("\nTop relevant documents (including zero scores):")
        if not results:
            print("No documents found.")
            return []

        # Display all documents
        for doc_name, score in results:
            print(f"Document: {doc_name}, Cosine Similarity Score: {score:.4f}")
        return results
