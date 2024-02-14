import os
import subprocess
import urllib.request

# Define the version of Solr
SOLR_VERSION = "9.4.0"

# Define the download URL
DOWNLOAD_URL = f"https://archive.apache.org/dist/lucene/solr/{SOLR_VERSION}/solr-{SOLR_VERSION}.tgz"

# Download Solr
urllib.request.urlretrieve(DOWNLOAD_URL, f'solr-{SOLR_VERSION}.tgz')

# Extract the downloaded file
subprocess.run(['tar', 'xzf', f'solr-{SOLR_VERSION}.tgz'])

# Print success message
print(f"Solr {SOLR_VERSION} has been downloaded and installed successfully.")

# Start Solr
subprocess.run(['solr-{SOLR_VERSION}/bin/solr', 'start'])
