from collections import defaultdict


class InvertedIndex:
    def __init__(self):
        self.index = defaultdict(list)

    def build_index(self, final_terms_docs):
        for doc_id, terms in final_terms_docs.items():

            for term in terms:

                if doc_id not in self.index[term]:
                    self.index[term].append(doc_id)

        return self.index

    def search(self, term):
        term = term.lower()
        return self.index.get(term, [])

    def boolean_and(self, term1, term2):
        docs1 = set(self.search(term1))
        docs2 = set(self.search(term2))

        return sorted(list(docs1 & docs2))

    def boolean_or(self, term1, term2):
        docs1 = set(self.search(term1))
        docs2 = set(self.search(term2))

        return sorted(list(docs1 | docs2))

    def boolean_not(self, term, all_docs):
        docs = set(self.search(term))

        return sorted(list(set(all_docs) - docs))

    def boolean_query(self, query, all_docs):
        tokens = query.lower().split()

        if len(tokens) == 1:
            return self.search(tokens[0])

        elif len(tokens) == 3:
            term1, operator, term2 = tokens

            if operator == "and":
                return self.boolean_and(term1, term2)

            elif operator == "or":
                return self.boolean_or(term1, term2)

        elif len(tokens) == 4:
            term1, operator1, operator2, term2 = tokens

            if operator1 == "and" and operator2 == "not":
                docs1 = set(self.search(term1))
                docs2 = set(self.search(term2))

                return sorted(list(docs1 - docs2))

        return []