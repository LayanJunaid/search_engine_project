from collections import defaultdict


class PositionalIndex:
    def __init__(self):
        self.index = defaultdict(lambda: defaultdict(list))

    def build_index(self, final_terms_docs):
        for doc_id, terms in final_terms_docs.items():

            for position, term in enumerate(terms):
                self.index[term][doc_id].append(position)

        return self.index

    def phrase_search(self, phrase_terms):
        if not phrase_terms:
            return []

        first_term = phrase_terms[0]

        if first_term not in self.index:
            return []

        candidate_docs = set(self.index[first_term].keys())

        for term in phrase_terms[1:]:

            if term not in self.index:
                return []

            candidate_docs = candidate_docs.intersection(
                set(self.index[term].keys())
            )

        matching_docs = []

        for doc_id in candidate_docs:
            first_positions = self.index[first_term][doc_id]

            for start_pos in first_positions:
                found = True

                for offset, term in enumerate(phrase_terms[1:], start=1):

                    expected_position = start_pos + offset

                    if expected_position not in self.index[term][doc_id]:
                        found = False
                        break

                if found:
                    matching_docs.append(doc_id)
                    break

        return sorted(matching_docs)