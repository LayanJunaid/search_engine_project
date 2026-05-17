class SpellCorrector:
    def __init__(self, vocabulary):
        self.vocabulary = set(vocabulary)

    def generate_ngrams(self, word, n=3):
        word = f"${word}$"

        ngrams = []

        for i in range(len(word) - n + 1):
            ngrams.append(word[i:i+n])

        return set(ngrams)

    def jaccard_similarity(self, set1, set2):
        intersection = len(set1 & set2)
        union = len(set1 | set2)

        if union == 0:
            return 0

        return intersection / union

    def edit_distance(self, word1, word2):
        m = len(word1)
        n = len(word2)

        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            dp[i][0] = i

        for j in range(n + 1):
            dp[0][j] = j

        for i in range(1, m + 1):
            for j in range(1, n + 1):

                if word1[i - 1] == word2[j - 1]:
                    cost = 0
                else:
                    cost = 1

                dp[i][j] = min(
                    dp[i - 1][j] + 1,
                    dp[i][j - 1] + 1,
                    dp[i - 1][j - 1] + cost
                )

        return dp[m][n]

    def get_candidates(self, word, threshold=0.3):
        word_ngrams = self.generate_ngrams(word)

        candidates = []

        for vocab_word in self.vocabulary:
            vocab_ngrams = self.generate_ngrams(vocab_word)

            similarity = self.jaccard_similarity(
                word_ngrams,
                vocab_ngrams
            )

            if similarity >= threshold:
                candidates.append(vocab_word)

        return candidates

    def suggest_word(self, word):
        BOOLEAN_OPERATORS = {"and", "or", "not"}

        if word.lower() in BOOLEAN_OPERATORS:
            return word

        if word in self.vocabulary:
            return word

        candidates = self.get_candidates(word)

        if not candidates:
            return word

        best_word = word
        best_distance = float("inf")

        for candidate in candidates:
            distance = self.edit_distance(word, candidate)

            if distance < best_distance:
                best_distance = distance
                best_word = candidate

        return best_word

    def correct_query(self, query_terms):
        corrected_terms = []

        for term in query_terms:
            corrected_terms.append(self.suggest_word(term))

        return corrected_terms