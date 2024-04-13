import os
import subprocess
import urllib.request
import argparse

from ..retriever.solr_index_docs import SolrIndex

#urls = https://www.nbcnews.com/pop-culture/davine-joy-randolph-oscar-win-best-supporting-actress-holdovers-rcna142112,https://www.nbcnews.com/news/kate-uks-princess-wales-issues-first-message-undergoing-surgery-rcna142641

def add_seed(core_name, urls):
    
    solrindex = SolrIndex(data_path=None, core=core_name)
    solr_base_url = f"http://localhost:8983/solr/{core_name}"
    json_objects = []
    
    urls = urls.split(",")
    print("type of urls: ", type(urls))
    print(urls, len(urls))
     
    for url in urls:
        data = {"url": url, "fetch_depth": 0, "status": "UNFETCHED"}
        json_objects.append(data)
    
    solrindex.index_docs(solr_base_url, json_objects)
    solrindex.commit(solr_url=solr_base_url)
        

def main():
    args = parse_args()
    add_seed(args["core"], args["urls"])

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--core", help="Give the solr core name", required=True)
    parser.add_argument("--urls", help="Give the urls name", required=True)
    args = parser.parse_args()
    return vars(args)

if __name__ == "__main__":
    main()
