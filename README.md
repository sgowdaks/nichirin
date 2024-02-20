# Nichirin: Simplified Data Indexing with Apache Solr

## Overview
**Nichirin** is a powerful tool designed to streamline data indexing using **Apache Solr**. If you're dealing with large datasets and need efficient search capabilities, Nichirin has got you covered. Here's what you need to know:

1. **What is Nichirin?**
   - **Nichirin** acts as a surface or layer on top of **Apache Solr**, making data indexing a breeze.
   - It abstracts away the complexities of Solr indexing, allowing users to focus on providing their data without worrying about the nitty-gritty details.

2. **Key Features:**
   - **Effortless Indexing**: Users simply provide their data and follow a few straightforward commands mentioned in the documentation.
   - **Automated Handling**: Nichirin takes care of the indexing process, ensuring optimal performance and efficiency.
   - **Seamless Integration**: Nichirin seamlessly integrates with your existing Solr setup, enhancing its capabilities.

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

Contributing and Feedback:
We welcome contributions! If you’d like to enhance Nichirin or report issues, feel free to submit a pull request.
For feedback or questions, open an issue on our GitHub repository.
