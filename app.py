import streamlit as st

from preprocessing import Preprocessor
from inverted_index import InvertedIndex
from incidence_matrix import IncidenceMatrix
from positional_index import PositionalIndex
from ranking import RankedRetrieval
from smart_query import QueryExpansion
from spell_correction import SpellCorrector


st.set_page_config(page_title="Medical Search Engine", layout="wide")

def extract_drug_name_from_doc_id(doc_id):
    """
    Example:
    doc8_azee_500_tablet.txt
    ->
    azee 500 tablet
    """

    filename = doc_id

    if filename.endswith(".txt"):
        filename = filename[:-4]

    parts = filename.split("_")

    drug_parts = parts[1:]

    drug_name = " ".join(drug_parts)

    return drug_name


def extract_section(lines, section_name):
    for i, line in enumerate(lines):
        if line.lower().startswith(section_name.lower()):
            if i + 1 < len(lines):
                return lines[i + 1].strip()
    return ""


def generate_snippet(text, query_terms, window=140):
    if not text:
        return ""

    text_clean = " ".join(text.split())
    text_lower = text_clean.lower()

    for term in query_terms:
        term = term.lower().strip()

        if not term:
            continue

        position = text_lower.find(term)

        if position != -1:
            start = max(0, position - window)
            end = min(len(text_clean), position + len(term) + window)

            snippet = text_clean[start:end]

            if start > 0:
                snippet = "..." + snippet

            if end < len(text_clean):
                snippet = snippet + "..."

            return snippet

    return text_clean[:300] + "..."


def display_ranked_result(doc_id, score, query_terms):
    text = st.session_state.display_documents.get(doc_id, "")
    drug_name = extract_drug_name_from_doc_id(doc_id)
    lines = text.splitlines()

    uses = extract_section(lines, "Uses")
    side_effects = extract_section(lines, "Side Effects")
    substitutes = extract_section(lines, "Substitutes")
    therapeutic_class = extract_section(lines, "Therapeutic Class")
    action_class = extract_section(lines, "Action Class")
    chemical_class = extract_section(lines, "Chemical Class")
    habit_forming = extract_section(lines, "Habit Forming")

    snippet = generate_snippet(text, query_terms)

    with st.expander(f"{doc_id} - {drug_name} | Score: {score}"):
        if snippet:
            st.write("**Document Snippet:**")
            st.info(snippet)

        if uses:
            st.write("**Uses:**")
            st.write(uses[:1000])

        if substitutes:
            st.write("**Substitutes:**")
            st.write(substitutes[:1000])

        if therapeutic_class:
            st.write("**Therapeutic Class:**")
            st.write(therapeutic_class)

        if action_class:
            st.write("**Action Class:**")
            st.write(action_class)

        if chemical_class:
            st.write("**Chemical Class:**")
            st.write(chemical_class)

        if habit_forming:
            st.write("**Habit Forming:**")
            st.write(habit_forming)

        if side_effects:
            st.write("**Side Effects:**")
            st.write(side_effects[:1000])

        st.write("**Full Document:**")
        st.write(text)


def extract_substitutes_from_doc(doc_id):
    text = st.session_state.display_documents.get(doc_id, "")
    lines = text.splitlines()

    substitutes_text = extract_section(lines, "Substitutes")

    if not substitutes_text:
        return []

    return [
        item.strip()
        for item in substitutes_text.split(",")
        if item.strip()
    ]


def extract_drug_name_from_substitute_query(query):
    query = query.lower()

    patterns = [
        "substitutes of",
        "substitute of",
        "alternatives of",
        "alternative of",
        "substitutes for",
        "substitute for",
        "alternatives for",
        "alternative for"
    ]

    for pattern in patterns:
        if pattern in query:
            return query.replace(pattern, "").strip()

    return query.strip()


def prepare_query(query):
    raw_terms = query.lower().split()

    spell_corrector = SpellCorrector(
        st.session_state.ranking.vocabulary
    )

    corrected_terms = spell_corrector.correct_query(raw_terms)
    corrected_query = " ".join(corrected_terms)

    query_terms = preprocessor.preprocess_text(corrected_query)["final_terms"]

    expander = QueryExpansion()
    expanded_terms = expander.expand_terms(query_terms)

    return corrected_query, query_terms, expanded_terms


def retrieve_best_matching_document(query_text):
    corrected_query, query_terms, expanded_terms = prepare_query(query_text)

    ranked_results = st.session_state.ranking.search(expanded_terms)

    if not ranked_results:
        return None, 0, corrected_query, expanded_terms

    best_doc_id, best_score = ranked_results[0]

    return best_doc_id, best_score, corrected_query, expanded_terms


def display_substitute_search(query):
    searched_drug = extract_drug_name_from_substitute_query(query)

    original_doc_id, original_score, corrected_drug_query, expanded_terms = retrieve_best_matching_document(
        searched_drug
    )

    if not original_doc_id:
        st.warning(f"No drug found for: {searched_drug}")
        return

    original_text = st.session_state.display_documents.get(original_doc_id, "")
    original_name = extract_drug_name_from_doc_id(original_doc_id)

    st.write(f"### Best Matching Drug: {original_name}")
    st.write(f"**Document ID:** {original_doc_id}")
    st.write(f"**Match Score:** {original_score}")

    substitutes = extract_substitutes_from_doc(original_doc_id)

    if not substitutes:
        st.warning("No substitutes found.")
        return

    st.write("### Substitute Names")
    st.write(substitutes)

    st.write("### Substitute Documents")

    found_any = False

    for substitute_name in substitutes:
        substitute_doc_id, substitute_score, corrected_substitute_query, substitute_terms = retrieve_best_matching_document(
            substitute_name
        )

        if substitute_doc_id:
            found_any = True

            display_ranked_result(
                substitute_doc_id,
                score=f"Substitute match: {substitute_score}",
                query_terms=substitute_terms
            )

    if not found_any:
        st.info("Substitute names were found, but no matching documents were retrieved.")


default_values = {
    "loaded": False,
    "processed": False,
    "indexes_built": False,
    "documents": {},
    "display_documents": {},
    "processed_documents": {},
    "final_terms_docs": {},
    "positional_terms_docs": {},
    "inverted_index": None,
    "incidence_matrix": None,
    "positional_index": None,
    "ranking": None,
}

for key, value in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = value


st.sidebar.title("☰ Menu")

page = st.sidebar.radio(
    "Navigation",
    [
        "Home Search",
        "Preprocessing Demo",
        "Index Samples",
        "Advanced Search",
        "Project Summary"
    ]
)

st.sidebar.divider()
st.sidebar.header("⚙️ System Controls")

documents_path = st.sidebar.text_input("Search documents folder", "documents")
display_documents_path = st.sidebar.text_input("Display documents folder", "display_documents")
use_stemming = st.sidebar.checkbox("Use Stemming", value=True)

preprocessor = Preprocessor(use_stemming=use_stemming)


if st.sidebar.button("1. Load Documents"):
    try:
        st.session_state.documents = preprocessor.load_documents(documents_path)
        st.session_state.display_documents = preprocessor.load_documents(display_documents_path)

        st.session_state.loaded = True
        st.session_state.processed = False
        st.session_state.indexes_built = False

        st.sidebar.success(f"Loaded {len(st.session_state.documents)} documents.")

    except Exception as e:
        st.sidebar.error(str(e))


if st.sidebar.button("2. Preprocess Documents"):
    if not st.session_state.loaded:
        st.sidebar.warning("Please load documents first.")
    else:
        st.session_state.processed_documents = preprocessor.preprocess_documents(
            st.session_state.documents
        )

        st.session_state.final_terms_docs = preprocessor.get_final_terms_only(
            st.session_state.processed_documents
        )

        st.session_state.positional_terms_docs = preprocessor.get_positional_terms_docs(
            st.session_state.documents
        )

        st.session_state.processed = True
        st.session_state.indexes_built = False

        st.sidebar.success("Preprocessing completed.")


if st.sidebar.button("3. Build Indexes"):
    if not st.session_state.processed:
        st.sidebar.warning("Please preprocess documents first.")
    else:
        inverted_index = InvertedIndex()
        inverted_index.build_index(st.session_state.final_terms_docs)

        incidence_matrix = IncidenceMatrix()
        incidence_matrix.build_matrix(st.session_state.final_terms_docs)

        positional_index = PositionalIndex()
        positional_index.build_index(st.session_state.positional_terms_docs)

        ranking = RankedRetrieval()
        ranking.build_model(st.session_state.final_terms_docs)

        st.session_state.inverted_index = inverted_index
        st.session_state.incidence_matrix = incidence_matrix
        st.session_state.positional_index = positional_index
        st.session_state.ranking = ranking

        st.session_state.indexes_built = True

        st.sidebar.success("Indexes built successfully.")


if page == "Home Search":
    st.title("💊 Medical Search Engine")
    st.caption("Search medicines by name, use, substitute, or related medical terms.")

    if not st.session_state.indexes_built:
        st.info("Use the sidebar to load documents, preprocess them, and build indexes first.")
    else:
        main_query = st.text_input(
            "Search",
            placeholder="Example: medicine used for fever"
        )

        if st.button("Search", type="primary") and main_query:
            corrected_query, query_terms, expanded_terms = prepare_query(main_query)

            st.write("### Corrected Query")
            st.write(corrected_query)

            st.write("### Ranked Results")

            results = st.session_state.ranking.search(expanded_terms)

            if results:
                for doc_id, score in results[:10]:
                    display_ranked_result(doc_id, score, expanded_terms)
            else:
                st.write("No documents found.")


elif page == "Preprocessing Demo":
    st.header("Preprocessing Demonstration")

    if not st.session_state.loaded:
        st.info("Load documents first.")
    else:
        doc_ids = list(st.session_state.documents.keys())

        selected_doc = st.selectbox(
            "Choose a document",
            doc_ids
        )

        st.subheader("Original Text")

        st.text_area(
            "Original Document",
            st.session_state.documents[selected_doc],
            height=250
        )

        if st.session_state.processed:
            data = st.session_state.processed_documents[selected_doc]

            st.subheader("Processed Version")

            processed_text = " ".join(data["final_terms"])

            st.text_area(
                "Processed Document",
                processed_text,
                height=250
            )

            st.write("### Statistics")

            col1, col2, col3 = st.columns(3)

            col1.metric("Original Tokens", len(data["tokens"]))
            col2.metric("Final Terms", len(data["final_terms"]))
            col3.metric("Unique Terms", len(set(data["final_terms"])))


elif page == "Index Samples":
    st.header("Index Samples")

    if not st.session_state.indexes_built:
        st.info("Build indexes first.")
    else:
        index_type = st.selectbox(
            "Choose index",
            [
                "Inverted Index",
                "Incidence Matrix",
                "Positional Index"
            ]
        )

        if index_type == "Inverted Index":
            st.subheader("Inverted Index Sample")

            rows = []

            for i, (term, docs) in enumerate(st.session_state.inverted_index.index.items()):
                rows.append({
                    "Term": term,
                    "Document Frequency": len(docs),
                    "Posting List": docs
                })

                if i >= 20:
                    break

            st.dataframe(rows, use_container_width=True)

        elif index_type == "Incidence Matrix":
            st.subheader("Incidence Matrix Sample")

            sample = st.session_state.incidence_matrix.get_sample(15)
            st.dataframe(sample, use_container_width=True)

        elif index_type == "Positional Index":
            st.subheader("Positional Index Sample")

            rows = []

            for i, (term, postings) in enumerate(st.session_state.positional_index.index.items()):
                rows.append({
                    "Term": term,
                    "Positions": dict(postings)
                })

                if i >= 20:
                    break

            st.dataframe(rows, use_container_width=True)


elif page == "Advanced Search":
    st.header("Advanced Search")

    if not st.session_state.indexes_built:
        st.info("Load, preprocess, and build indexes first.")
    else:
        search_type = st.selectbox(
            "Choose Retrieval Type",
            [
                "Boolean Search",
                "Incidence Matrix Search",
                "Phrase Search",
                "Ranked Retrieval",
                "Substitute Search"
            ]
        )

        query = st.text_input("Enter your query")

        if st.button("Search") and query:
            corrected_query, query_terms, expanded_terms = prepare_query(query)

            st.write("### Corrected Query")
            st.write(corrected_query)

            if search_type == "Boolean Search":
                results = st.session_state.inverted_index.boolean_query(
                    corrected_query,
                    st.session_state.documents.keys()
                )

                st.write("### Results")
                st.write(results if results else "No documents found.")

            elif search_type == "Incidence Matrix Search":
                results = st.session_state.incidence_matrix.query(corrected_query)

                st.write("### Results")
                st.write(results if results else "No documents found.")

            elif search_type == "Phrase Search":
                phrase_terms = preprocessor.preprocess_for_positional_index(
                    corrected_query.replace('"', "")
                )

                results = st.session_state.positional_index.phrase_search(phrase_terms)

                st.write("### Processed Phrase Terms")
                st.write(phrase_terms)

                st.write("### Results")
                st.write(results if results else "No documents found.")

            elif search_type == "Ranked Retrieval":
                st.write("### Expanded Query Terms")
                st.write(expanded_terms)

                results = st.session_state.ranking.search(expanded_terms)

                st.write("### Ranked Results")

                if results:
                    for doc_id, score in results[:10]:
                        display_ranked_result(doc_id, score, expanded_terms)
                else:
                    st.write("No documents found.")

            elif search_type == "Substitute Search":
                st.write("### Substitute Search Results")
                display_substitute_search(corrected_query)


elif page == "Project Summary":
    st.header("Project Summary")

    st.write("""
    This system is a Mini Medical Search Engine built using Python and Streamlit.

    It supports:
    - Document loading
    - Document preprocessing
    - Incidence matrix
    - Inverted index
    - Positional index
    - Boolean retrieval
    - Phrase search
    - TF-IDF ranked retrieval
    - Cosine similarity
    - Spelling correction
    - Query expansion
    - Document snippets
    - Retrieval-based substitute search
    """)

    st.write("""
    The home page uses Ranked Retrieval by default.
    Advanced Search provides access to Boolean Search, Incidence Matrix Search,
    Phrase Search, Ranked Retrieval, and Substitute Search.
    """)