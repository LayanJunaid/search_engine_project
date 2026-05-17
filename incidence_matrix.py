# incidence_matrix.py

class IncidenceMatrix:
    def __init__(self):
        self.vocabulary = []
        self.documents = []
        self.matrix = {}

    def build_matrix(self, final_terms_docs):
        self.documents = sorted(final_terms_docs.keys())

        vocabulary_set = set()
        for terms in final_terms_docs.values():
            vocabulary_set.update(terms)

        self.vocabulary = sorted(vocabulary_set)

        for term in self.vocabulary:
            self.matrix[term] = []

            for doc_id in self.documents:
                if term in final_terms_docs[doc_id]:
                    self.matrix[term].append(1)
                else:
                    self.matrix[term].append(0)

        return self.matrix

    def search_term(self, term):
        term = term.lower()

        if term not in self.matrix:
            return []

        row = self.matrix[term]
        return self._row_to_docs(row)

    def boolean_and(self, term1, term2):
        row1 = self.matrix.get(term1.lower(), [0] * len(self.documents))
        row2 = self.matrix.get(term2.lower(), [0] * len(self.documents))

        result_row = [
            1 if a == 1 and b == 1 else 0
            for a, b in zip(row1, row2)
        ]

        return self._row_to_docs(result_row)

    def boolean_or(self, term1, term2):
        row1 = self.matrix.get(term1.lower(), [0] * len(self.documents))
        row2 = self.matrix.get(term2.lower(), [0] * len(self.documents))

        result_row = [
            1 if a == 1 or b == 1 else 0
            for a, b in zip(row1, row2)
        ]

        return self._row_to_docs(result_row)

    def boolean_not(self, term):
        row = self.matrix.get(term.lower(), [0] * len(self.documents))

        result_row = [
            1 if value == 0 else 0
            for value in row
        ]

        return self._row_to_docs(result_row)

    def query(self, user_query):
        tokens = user_query.lower().split()

        if len(tokens) == 0:
            return []

        if len(tokens) == 1:
            return self.search_term(tokens[0])

        if len(tokens) == 2 and tokens[0] == "not":
            return self.boolean_not(tokens[1])

        if len(tokens) == 3:
            term1, operator, term2 = tokens

            if operator == "and":
                return self.boolean_and(term1, term2)

            if operator == "or":
                return self.boolean_or(term1, term2)

        if len(tokens) == 4:
            term1, operator1, operator2, term2 = tokens

            if operator1 == "and" and operator2 == "not":
                docs1 = set(self.search_term(term1))
                docs2 = set(self.search_term(term2))
                return sorted(list(docs1 - docs2))

        return []

    def _row_to_docs(self, row):
        result_docs = []

        for i, value in enumerate(row):
            if value == 1:
                result_docs.append(self.documents[i])

        return result_docs

    def get_sample(self, n=10):
        sample = []

        for term in self.vocabulary[:n]:
            row = {"Term": term}

            for i, doc_id in enumerate(self.documents):
                row[doc_id] = self.matrix[term][i]

            sample.append(row)

        return sample

    def print_sample(self, n=10):
        print("\n--- Incidence Matrix Sample ---")

        header = "Term".ljust(15) + " ".join(self.documents)
        print(header)
        print("-" * len(header))

        for term in self.vocabulary[:n]:
            row_values = " ".join(
                str(value).ljust(4)
                for value in self.matrix[term]
            )

            print(term.ljust(15) + row_values)