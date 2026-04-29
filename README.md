# 💊 Smart Pharmacy Search Engine

A Python-based mini search engine for pharmacy-related documents.  
The project applies core Information Retrieval techniques such as preprocessing, incidence matrix, inverted index, positional index, Boolean retrieval, TF-IDF, and cosine similarity.

---

## 📌 Project Idea

This project is a smart search engine for medicine documents.  
Each document represents one medicine and contains information about:

- medicine uses
- symptoms treated
- warnings
- side effects
- related medical terms

Users can search inside the medicine collection using different retrieval methods.

---

## 🎯 Objectives

- Build a searchable document collection
- Apply text preprocessing techniques
- Implement multiple indexing methods
- Support Boolean and phrase queries
- Rank documents using TF-IDF and cosine similarity
- Display preprocessing and retrieval results clearly

---

## 🧾 Dataset

The dataset contains 20 text documents stored in the `documents/` folder.

Each file represents one medicine, for example:

```text
doc1_paracetamol.txt
doc2_ibuprofen.txt
doc3_aspirin.txt
...

The dataset is written in English and designed to include repeated and meaningful terms such as:

fever, pain, cough, stomach, side effects, children, allergy, infection
🧹 Preprocessing Steps

Before indexing, each document is processed using:

Case folding
Punctuation removal
Tokenization
Stop-word removal
Stemming

Example:

Original:
Paracetamol is used to reduce fever and relieve mild pain.

Final terms:
['paracetamol', 'use', 'reduc', 'fever', 'reliev', 'mild', 'pain']
🔎 Search Methods
1. Incidence Matrix

Represents terms and documents using binary values:

1 = term exists in document
0 = term does not exist
2. Inverted Index

Stores each term with the documents where it appears.

Example:

fever -> doc1, doc2, doc3, doc15
3. Positional Index

Stores the exact positions of each term inside documents.
This allows phrase search.

Example:

"side effects"
4. Boolean Retrieval

Supports:

AND
OR
NOT

Example queries:

fever AND pain
cough OR allergy
pain AND NOT stomach
5. Ranked Retrieval

Uses:

TF-IDF
Cosine Similarity

Documents are ranked from most relevant to least relevant.

Example query:

child fever vomiting
📂 Project Structure
search_engine_project/
│
├── documents/
│   ├── doc1_paracetamol.txt
│   ├── doc2_ibuprofen.txt
│   └── ...
│
├── main.py
├── preprocessing.py
├── incidence_matrix.py
├── inverted_index.py
├── positional_index.py
├── ranking.py
├── utils.py
│
├── README.md
└── report.pdf
🛠️ Technologies Used
Python
NLTK
Regular Expressions
Collections
Math
Pandas / NumPy optional
▶️ How to Run
1. Install requirements
pip install nltk
2. Download NLTK resources
import nltk
nltk.download("punkt")
nltk.download("stopwords")

If needed:

nltk.download("punkt_tab")
3. Run the program
python main.py
🧪 Example Queries
fever AND pain
"side effects"
stomach pain
cough syrup
blood sugar
📊 Expected Output

The system displays:

original and processed documents
incidence matrix
inverted index posting lists
positional index data
Boolean search results
phrase search results
ranked results with similarity scores

Example ranked result:

Query: fever pain

Rank 1: doc1_paracetamol.txt | Score: 0.82
Rank 2: doc2_ibuprofen.txt   | Score: 0.76
Rank 3: doc15_naproxen.txt   | Score: 0.69
⭐ Bonus Features Planned
Spelling correction
Query expansion
Document snippets
Web interface using React
Evaluation metrics: Precision, Recall, F1-score
