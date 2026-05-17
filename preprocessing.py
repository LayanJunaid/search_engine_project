import os
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize


class Preprocessor:
    def __init__(self, use_stemming=True):
        self.use_stemming = use_stemming
        self.stop_words = set(stopwords.words("english"))
        self.stemmer = PorterStemmer()

    def load_documents(self, folder_path):
        documents = {}

        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        for filename in sorted(os.listdir(folder_path)):
            if filename.endswith(".txt"):
                file_path = os.path.join(folder_path, filename)

                with open(file_path, "r", encoding="utf-8") as file:
                    doc_id = filename.split("_")[0]
                    documents[doc_id] = file.read()

        return documents

    def case_folding(self, text):
        return text.lower()

    def remove_punctuation(self, text):
        return re.sub(r"[^a-zA-Z0-9\s]", " ", text)

    def tokenize(self, text):
        return word_tokenize(text)

    def remove_stopwords(self, tokens):
        return [
            token for token in tokens
            if token not in self.stop_words and len(token) > 1
        ]

    def apply_stemming(self, tokens):
        return [self.stemmer.stem(token) for token in tokens]

    def preprocess_text(self, text):
        lowercase_text = self.case_folding(text)

        cleaned_text = self.remove_punctuation(lowercase_text)

        tokens = self.tokenize(cleaned_text)

        tokens_without_stopwords = self.remove_stopwords(tokens)

        if self.use_stemming:
            final_terms = self.apply_stemming(tokens_without_stopwords)
        else:
            final_terms = tokens_without_stopwords

        return {
            "lowercase_text": lowercase_text,
            "cleaned_text": cleaned_text,
            "tokens": tokens,
            "tokens_without_stopwords": tokens_without_stopwords,
            "final_terms": final_terms
        }

    def preprocess_for_positional_index(self, text):
        lowercase_text = self.case_folding(text)

        cleaned_text = self.remove_punctuation(lowercase_text)

        tokens = self.tokenize(cleaned_text)

        if self.use_stemming:
            final_terms = self.apply_stemming(tokens)
        else:
            final_terms = tokens

        return final_terms

    def preprocess_documents(self, documents):
        processed_documents = {}

        for doc_id, original_text in documents.items():
            result = self.preprocess_text(original_text)

            processed_documents[doc_id] = {
                "original_text": original_text,
                **result
            }

        return processed_documents

    def get_final_terms_only(self, processed_documents):
        final_terms_docs = {}

        for doc_id, data in processed_documents.items():
            final_terms_docs[doc_id] = data["final_terms"]

        return final_terms_docs

    def get_positional_terms_docs(self, documents):
        positional_terms_docs = {}

        for doc_id, text in documents.items():
            positional_terms_docs[doc_id] = self.preprocess_for_positional_index(text)

        return positional_terms_docs