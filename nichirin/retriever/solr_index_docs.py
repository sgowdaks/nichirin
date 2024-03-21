#!/usr/bin/env python
import requests
import json
import time
import torch
import json
import argparse
import os

from pathlib import Path

class SolrIndex:
    # url = 'http://localhost:8983/solr/wiki/update'
    def __init__(self, data_path, core):
        self.batch_size = 1000
        self.headers = {"Content-Type": "application/json"}
        self.data_path = data_path
        self.wikidata_path = Path(self.data_path) if self.data_path else None
        self.solr_url = "http://localhost:8983/solr/" + core

    def read_(self):
        stream = self.read_docs(self.data_path)
        self.index_docs(solr_url=self.solr_url, stream=stream)
        self.commit(solr_url=self.solr_url)

    def read_docs(self, path):
        print(f"reading docs from {path}")
        skips = 0
        count = 0
        tok_file = [f for f in self.wikidata_path.glob("*.split")][0]
        ten_file = [f for f in self.wikidata_path.glob("*.pt")][0]
        tensor_exists = False
        
        if len(ten_file) > 0:
            tensor = torch.load(ten_file)
            tensor_exists = True
        
        with open(tok_file) as lines:
            for line in lines:
                data = json.load(line)
                count += 1
                
                if tensor_exists:
                    data["vector"] = tensor[count].tolist()
                    
                json_string = data
                yield json_string
                            
        print(f"Skips={skips}, Good={count}")
                   

    def make_batches(self, stream, batch_size):
        print(f"making batches of batch={batch_size}")
        buffer = []
        for it in stream:
            buffer.append(it)
            if len(buffer) >= batch_size:
                yield buffer
                buffer = []
        if buffer:
            yield buffer

    def index_docs(self, solr_url, stream):
        print(f"indexing docs to {solr_url}")
        
        update_url = solr_url.rstrip("/") + "/update"
        
        if isinstance(stream, list):
            data = dict(add=stream)
            time.sleep(0.5)
            response = requests.post(
                update_url, headers=self.headers, data=json.dumps(data)
            )
            if response.status_code != 200:
                raise Exception(response.text)
            now_t = time.time()
        else:            
            batches = self.make_batches(stream, batch_size=self.batch_size)
            count = 0
            last_t = time.time()
            for batch in batches:
                count += len(batch)
                data = dict(add=batch)
                time.sleep(0.5)
                response = requests.post(
                    update_url, headers=self.headers, data=json.dumps(data)
                )
                if response.status_code != 200:
                    raise Exception(response.text)
                now_t = time.time()
                if now_t - last_t > 2:
                    print(f"docs= {count:,}")
                    last_t = now_t
            print(f"Total docs= {count:,}")

    def commit(self, solr_url):
        print("Committing docs ")
        commit_url = solr_url.rstrip("/") + "/update"
        data = {"commit": {}}
        response = requests.post(
            commit_url, headers=self.headers, data=json.dumps(data)
        )
        print(response.status_code, response.text)
        assert response.status_code == 200
        
def main():  
    args = parse_args()
    si = SolrIndex(args["data_path"], args["core"])
    si.read_()
    
    
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-path",
        type=Path,
        required=True,
        help="Give the input file path",
    )
    parser.add_argument("--core", help="Give the solr core name", required=True)
    args = parser.parse_args()
    return vars(args)


if __name__ == "__main__":
    main()
