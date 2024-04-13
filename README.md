# Nichirin: A custom search framework featuring augmented generation with retrieval capabilities.

## Overview
**Nichirin** serves as an advanced layer atop Apache Solr, facilitating seamless data indexing operations.

1. **What is Nichirin?**
   - **Nichirin** acts as a surface or layer on top of **Apache Solr**, making data indexing a breeze.
   - It abstracts away the complexities of Solr indexing, allowing users to focus on providing their data without worrying about the nitty-gritty details.

2. **Key Features:**
   - **Multi-level Crawling**: Performs multi-level web crawling utilizing a depth-first search methodology, with text indexing and retrieval facilitated through Apache Solr.
   - **Efficient Indexing**: Integrated Apache Spark for parallel processing of URLs, improving the scalability and efficiency of both web crawling and text indexing.
   - **Python package**: Available as a Python package on PyPI for easy installation and integration

<!-- '''3. **Getting Started:**
   - **Installation**: Clone this repository and follow the installation instructions in the Installation Guide.
   - **Usage**:
     - Execute `nichirin.py`.
     - Input your data or specify the data source.
     - Follow the provided commands to initiate indexing.
     - Sit back and let Nichirin handle the rest!

4. **Example Usage:**
   ```bash
   $ python nichirin.py
   Welcome to Nichirin!
   Please provide your data source (CSV, JSON, or database connection string):
   > data.csv
   Data source accepted. Initializing indexing...
   Indexing complete! Your data is now searchable via Solr.  -->
   
## Commands
<!-- pipeline = "nichirin.pipeline:main" -->
* `install-solr` to install solr
* `create-core --core <core name>` to create solr core, 
* `partition-data --path <path to the dataset>` to partition the data
* `pipeline --path <path to the dataset>` generate embeddings of the partition data
* `index-solr --data-path <path to dataset> --core <core to which the data needs to be sent>` index the data  
* `query-solr --input_sen <input sen> --core_name <core name to query from>` query the data from solr

## Quickstart
* Once after setting up the solr, creating cores run `seed-urls --core <core name> --urls <urls separted with commas>` command to add seed urls
* Now that you have added seed urls, run `start-crawler` commad, this might take a while.
* Once the crawling is completed, to view the results run  the command `start-serve` this will start the flask web app.

Contributing and Feedback:
We welcome contributions! If you’d like to enhance Nichirin or report issues, feel free to submit a pull request.
For feedback or questions, open an issue on our GitHub repository.
