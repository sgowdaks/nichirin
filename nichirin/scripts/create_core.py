import os
import subprocess
import requests
import argparse

from pathlib import Path

def check_solr_status(SOLR_VERSION):
    
    solr_url = "http://localhost:8983/solr"
    try:
        response = requests.get(f"{solr_url}/admin/ping")
        check = response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        check = False
            
    if not check:
        subprocess.run([f'solr-{SOLR_VERSION}/bin/solr', 'start'])
    
def create_core(SOLR_VERSION, core_name):
        
    solr_dir = f"solr-{SOLR_VERSION}"
    subprocess.run([f"{solr_dir}/bin/solr", "create", "-c", core_name], check=True)

def main(): 
    args = parse_args()
    SOLR_VERSION = os.getenv('SOLR_VERSION', "9.1.1")
    check_solr_status(SOLR_VERSION)
    create_core(SOLR_VERSION, (args["core"]))
    
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--core", help="Give the solr core name", required=True)
    args = parser.parse_args()
    return vars(args)

if __name__ == "__main__":
    main()