#!/bin/bash

# Define the version of Solr
SOLR_VERSION="9.4.0"
export SOLR_VERSION

# Define the download URL
DOWNLOAD_URL="https://archive.apache.org/dist/lucene/solr/${SOLR_VERSION}/solr-${SOLR_VERSION}.tgz"

# Download Solr
wget ${DOWNLOAD_URL}

# Extract the downloaded file
tar xzf solr-${SOLR_VERSION}.tgz

# Move the extracted folder to /opt
sudo mv solr-${SOLR_VERSION} /opt/solr

# Print success message
echo "Solr ${SOLR_VERSION} has been downloaded and installed successfully."

/opt/solr/solr-${SOLR_VERSION}/bin/solr start