import requests
import csv
import json
api_url = "https://rest.uniprot.org/uniprotkb/search?query=*&size=20&format=json"
response = requests.get(api_url)
if response.status_code != 200:
    raise Exception(f"API request failed with status code {response.status_code}")

response_json = response.json()
def extract_required_fields(entry):
    """
    Extract required fields from a UniProt entry.
    """
    return {
        "entryType": entry.get("entryType", "N/A"),
        "primaryAccession": entry.get("primaryAccession", "N/A"),
        "secondaryAccessions": entry.get("secondaryAccessions", []),
        "uniProtkbId": entry.get("uniProtkbId", "N/A"),
        "entryAudit": entry.get("entryAudit", {}),
        "organism": entry.get("organism", {}),
        "proteinExistence": entry.get("proteinExistence", "N/A"),
        "proteinDescription": entry.get("proteinDescription", {}),
        "genes": entry.get("genes", []),
        "Functions": [
            comment.get("texts", [{}])[0].get("value", "N/A")
            for comment in entry.get("comments", [])
            if comment.get("commentType") == "FUNCTION" and comment.get("texts")
        ],
        "Miscellaneous": [
            comment.get("texts", [{}])[0].get("value", "N/A")
            for comment in entry.get("comments", [])
            if comment.get("commentType") == "MISCELLANEOUS" and comment.get("texts")
        ],
    }

entries = response_json.get("results", [])
data = [extract_required_fields(entry) for entry in entries]

csv_file = "uniprot_data.csv"
with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=[
        "entryType", 
        "primaryAccession", 
        "secondaryAccessions", 
        "uniProtkbId", 
        "entryAudit", 
        "organism", 
        "proteinExistence", 
        "proteinDescription", 
        "genes", 
        "Functions", 
        "Miscellaneous"
    ])
    writer.writeheader()
    for row in data:
        row["secondaryAccessions"] = json.dumps(row["secondaryAccessions"])
        row["entryAudit"] = json.dumps(row["entryAudit"])
        row["organism"] = json.dumps(row["organism"])
        row["proteinDescription"] = json.dumps(row["proteinDescription"])
        row["genes"] = json.dumps(row["genes"])
        row["Functions"] = json.dumps(row["Functions"])
        row["Miscellaneous"] = json.dumps(row["Miscellaneous"])
        writer.writerow(row)

print(f"Data has been written to {csv_file}")
