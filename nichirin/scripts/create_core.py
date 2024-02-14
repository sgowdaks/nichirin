import os
import subprocess
import requests

def check_solr_status(solr_url):
    try:
        response = requests.get(f"{solr_url}/admin/ping")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return False

# Replace with your Solr server URL
solr_url = "http://localhost:8983/solr"
is_solr_up = check_solr_status(solr_url)

SOLR_VERSION = os.getenv('SOLR_VERSION')

if not is_solr_up:
    subprocess.run(['solr-{SOLR_VERSION}/bin/solr', 'start'])
    

solr_dir = f"solr-{SOLR_VERSION}"

# Start Solr
subprocess.run([f"{solr_dir}/bin/solr", "start"], check=True)

# Get the core name from the user
core_name = input("Enter the core name: ")

# Use the Solr create command to create the core
subprocess.run([f"{solr_dir}/bin/solr", "create", "-c", core_name], check=True)
