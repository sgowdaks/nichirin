import requests

# Define the Solr URL
solr_url = "http://localhost:8983/solr/crawldb/update?commit=true"

# Define the delete query
delete_query = {
    "delete": {"query": "*:*"}
}

# Send a POST request to delete all documents
response = requests.post(solr_url, json=delete_query)

# Check if the request was successful
if response.status_code == 200:
    print("All documents in the Solr index have been deleted.")
else:
    print(f"Error deleting documents. Status code: {response.status_code}")
