import re
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pandas as pd
from langchain_ollama import OllamaLLM

import vectorizer
llm = OllamaLLM(model="llama3.1")
user_query = "Give me the information of the following protein: A0A0C5B5G6"

keywords = """
primaryAccession: A0JNW5 | secondaryAccessions: ["A0PJE5", "O75183", "Q8NDL1", "Q96C30", "Q9BTS5", "Q9H0F1"]
"""
# Load the SentenceTransformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Vectorize the keywords
query_vector = model.encode([keywords])

# Load the FAISS index
index = faiss.read_index("protein_vectors.index")

# Search FAISS
distances, indices = index.search(np.array(query_vector), k=3)

# Retrieve the most relevant rows using the indices
if len(indices) > 0:
    print("Top 3 Matching Rows and Their Scores:")
    for i in range(3):
        idx = indices[0][i]
        distance = distances[0][i]
        matching_row = vectorizer.concatenated_rows[idx]
        print(f"Score: {distance}")
        print(f"Row {i + 1}: {matching_row}") 
        print("-" * 50)
else:
    print("No matching result found in the index.")

