import faiss
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import pandas as pd
import vectorize_protobert  

# Load the FAISS index 
index_path = "protein_vectors1.index"
index = faiss.read_index(index_path)
print(f"Loaded FAISS index from {index_path}")

data_path = "uniprot_data.csv"
df = pd.read_csv(data_path)
print(f"Loaded data from {data_path}")

def retrieve_top_matches(query, k=3):
    # Encode the query using ProtTrans
    print(f"Encoding query: {query}")
    query_vector = vectorize_protobert.encode_prottrans([query], max_length=128)
    faiss.normalize_L2(query_vector)

    # Check dimension compatibility
    if query_vector.shape[1] != index.d:
        raise ValueError("Mismatch between query vector dimension and FAISS index dimension.")

    # Perform the search in the FAISS index
    print("Searching FAISS index...")
    distances, indices = index.search(query_vector, k=k)

    # Retrieve matching rows from the DataFrame
    matches = []
    for idx, dist in zip(indices[0], distances[0]):
        if idx < len(df):
            matches.append({"row": df.iloc[idx].to_dict(), "score": dist})
    return matches

# Example query
query = """
'A0A1B0GTW7'
"""
print(f"Query: {query}")
results = retrieve_top_matches(query, k=3)

# Display the results
print("\nTop Matches:")
for result in results:
    print(f"Score: {result['score']}")
    print(f"Row: {result['row']}")
    print("-" * 50)
