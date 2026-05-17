import math
from collections import Counter


class RankedRetrieval:
    def __init__(self):
        self.documents = {}
        self.vocabulary = set()

        self.tf = {}
        self.idf = {}
        self.tfidf = {}

    def build_model(self, final_terms_docs):
        self.documents = final_terms_docs

        for terms in final_terms_docs.values():
            self.vocabulary.update(terms)

        total_docs = len(final_terms_docs)

        # TF
        for doc_id, terms in final_terms_docs.items():
            self.tf[doc_id] = Counter(terms)

        # IDF
        for term in self.vocabulary:
            docs_containing_term = 0

            for terms in final_terms_docs.values():
                if term in terms:
                    docs_containing_term += 1

            self.idf[term] = math.log10(
                total_docs / (1 + docs_containing_term)
            )

        # TF-IDF
        for doc_id, term_counts in self.tf.items():
            self.tfidf[doc_id] = {}

            for term, freq in term_counts.items():
                self.tfidf[doc_id][term] = freq * self.idf[term]

    def build_query_vector(self, query_terms):
        query_tf = Counter(query_terms)

        query_vector = {}

        for term, freq in query_tf.items():

            if term in self.idf:
                query_vector[term] = freq * self.idf[term]

        return query_vector

    def cosine_similarity(self, query_vector, doc_vector):
        dot_product = 0

        for term, value in query_vector.items():

            if term in doc_vector:
                dot_product += value * doc_vector[term]

        query_magnitude = math.sqrt(
            sum(value ** 2 for value in query_vector.values())
        )

        doc_magnitude = math.sqrt(
            sum(value ** 2 for value in doc_vector.values())
        )

        if query_magnitude == 0 or doc_magnitude == 0:
            return 0

        return dot_product / (query_magnitude * doc_magnitude)

    def search(self, query_terms):
        query_vector = self.build_query_vector(query_terms)

        scores = []

        for doc_id, doc_vector in self.tfidf.items():
            similarity = self.cosine_similarity(query_vector, doc_vector)

            if similarity > 0:
                scores.append((doc_id, round(similarity, 4)))

        scores.sort(key=lambda x: x[1], reverse=True)

        return scores