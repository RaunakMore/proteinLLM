from langchain_ollama import OllamaLLM
import requests
import json
import response_process
from langchain.memory import ConversationBufferMemory

# Initialize the LLM
llm = OllamaLLM(model="llama3.2:1b")

# Initialize memory for conversation history
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Function to extract protein name from the user's query
def extract_protein_name(query_from_user):
  
    query_first = f"""The provided sentence is "{query_from_user}". Extract the protein id from the given sentence.
    Note: only give the protein ID, only one word for the protein Id, and do not give any other words in the response."""
    print(query_first)
    response = llm.invoke(query_first)
    print(response)
    protein_name = response.strip()
    print(protein_name)
    return protein_name

# Function to fetch protein data from UniProt API
def fetch_protein_context(protein_name):
    """
    Fetch protein context from the UniProt API. Returns a default context on exception.

    Args:
        protein_name (str): Protein name or UniProt ID.

    Returns:
        dict: Processed context data or a default error context.
    """
    api_end_point_prot1 = f"https://rest.uniprot.org/uniprotkb/{protein_name}"
    try:
        response_data = requests.get(api_end_point_prot1)

        if response_data.status_code == 200:
            response_json = response_data.json()
            
            # Extract required fields
            required_fields = {
                "entryType": response_json.get("entryType"),
                "primaryAccession": response_json.get("primaryAccession"),
                "secondaryAccessions": response_json.get("secondaryAccessions", []),
                "uniProtkbId": response_json.get("uniProtkbId"),
                "entryAudit": response_json.get("entryAudit"),
                "organism": response_json.get("organism"),
                "proteinExistence": response_json.get("proteinExistence"),
                "proteinDescription": response_json.get("proteinDescription"),
                "genes": response_json.get("genes", []),
                "Functions": [
                    comment.get("texts", [{}])[0].get("value", "N/A")
                    for comment in response_json.get("comments", [])
                    if comment.get("commentType") == "FUNCTION" and comment.get("texts")
                ],
                "Miscellaneous": [
                    comment.get("texts", [{}])[0].get("value", "N/A")
                    for comment in response_json.get("comments", [])
                    if comment.get("commentType") == "MISCELLANEOUS" and comment.get("texts")
                ],
            }
            
            # Preprocess the context data
            context = response_process.preprocess_protein_data(required_fields)
            return context

        else:
            raise Exception(f"Failed to fetch data (HTTP {response_data.status_code})")

    except Exception as e:
        # Log the error and return a default context
        print(f"Error fetching protein context: {e}")
        return {
            "error": True,
            "message": "Exception has occurred. Can you specify the protein ID for more information?"
        }


# Function to generate a response based on the user's query and protein context
def generate_response(query_from_user, context):
   
    followup_query = f"""Given the following context about a protein:
{context}

Answer the question: "{query_from_user}"."""
    
    response = llm.invoke(followup_query)
    return response

if __name__ == "__main__":
    print("This is model.py being executed directly.")
