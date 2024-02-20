import os
import subprocess
import urllib.request

def download_and_install_solr(solr_version):
    DOWNLOAD_URL = f"https://archive.apache.org/dist/solr/solr/{solr_version}/solr-{solr_version}.tgz"

    urllib.request.urlretrieve(DOWNLOAD_URL, f'solr-{solr_version}.tgz')

    subprocess.run(['tar', 'xzf', f'solr-{solr_version}.tgz'])

    print(f"Solr {solr_version} has been downloaded and installed successfully.")

def start_solr(solr_version):
    subprocess.run([f'solr-{solr_version}/bin/solr', 'start'])

def main(): 
    SOLR_VERSION = os.getenv('SOLR_VERSION', "9.1.1")
    download_and_install_solr(SOLR_VERSION)
    start_solr(SOLR_VERSION)

if __name__ == "__main__":
    main()
