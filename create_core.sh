#!/bin/bash

# Define the name of the core and the Solr directory
/opt/solr/solr-${SOLR_VERSION}/bin/solr start

echo "Enter the core name:"
read core

core_name=core
solr_dir="/opt/solr/solr-${SOLR_VERSION}"

# Navigate to the Solr directory
cd $solr_dir

# Use the Solr create command to create the core
./bin/solr create -c $core_name
