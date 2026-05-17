class QueryExpansion:
    def __init__(self):
        self.synonyms = {
            "fever": ["temperature", "heat"],
            "pain": ["ache", "relief"],
            "headache": ["migraine"],
            "cough": ["congestion", "syrup"],
            "vomiting": ["nausea"],
            "diabetes": ["insulin", "sugar"],
            "infection": ["bacterial", "antibiotic"]
        }

    def expand_terms(self, query_terms):
        expanded_terms = []

        for term in query_terms:
            expanded_terms.append(term)

            if term in self.synonyms:
                expanded_terms.extend(self.synonyms[term])

        unique_terms = []

        for term in expanded_terms:

            if term not in unique_terms:
                unique_terms.append(term)

        return unique_terms