import torch
import argparse
import requests
from typing import List
from datetime import date
from transformers import AutoTokenizer, AutoModel
from pathlib import Path

from nichirin.utils.data_utils import load_yaml
import logging

# Use GPU if available else revert to CPU
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class SolrRetriever:
    def __init__(self, logger=None, cfg=None) -> None:
        
        conf_path = Path(__file__).parent.parent / "confs/app.yaml"
        
        if not cfg:
            cfg = load_yaml(conf_path)
            print("cfg loaded")

        self.cfg = cfg
        self.retrieval_conf = self.cfg["retrieval"]
        self.retrieval_threshold = self.cfg["retrieval_threshold"]
        self.retrieval_top_k = self.cfg["retrieval_top_k"]

        # Load all available retrieval models separately
        self.retrieval_models = self.load_retrieval_models()
        print("Retrieval setup complete!\n")

    def load_retrieval_models(self) -> dict:
        self.retrieval_model_names = list(self.retrieval_conf.keys())
        
        print(f"Using {len(self.retrieval_model_names)} models for retrieval - {self.retrieval_model_names}")

        retrieval_models = {}
        for model_name in self.retrieval_model_names:
            (
                retrieval_models[model_name + "_model"],
                retrieval_models[model_name + "_tokenizer"],
            ) = self.load_single_model(self.retrieval_conf[model_name]["model_id"])

        # Return a dict of retrieval models and tokenizers      
        return retrieval_models

    def load_single_model(self, model_id: str):
        model = AutoModel.from_pretrained(model_id).to(DEVICE)
        tokenizer = AutoTokenizer.from_pretrained(model_id, model_max_length=1024)
        model = model.eval()
        torch.set_grad_enabled(False)
        print(f"Model and tokenizer for {model_id} loaded.")
        return model, tokenizer

    def mean_pooling(self, token_embeddings, mask):
        token_embeddings = token_embeddings.masked_fill(~mask[..., None].bool(), 0.0)
        sentence_embeddings = token_embeddings.sum(dim=1) / mask.sum(dim=1)[..., None]
        return sentence_embeddings

    def get_embeddings(self, text_list, model, tokenizer):
        inputs = tokenizer(
            text_list, padding=True, truncation=True, return_tensors="pt"
        ).to(DEVICE)
        outputs = model(**inputs)
        embeddings = self.mean_pooling(outputs[0], inputs["attention_mask"])
        return embeddings

    def retrieve_context(
        self, query, core_name, solr_url, model_name, char_limit=2400
    ) -> List[List[str]]:
        
        torch.set_grad_enabled(False)     
        embed = self.get_embeddings(
            query,
            model=self.retrieval_models[f"{model_name}_model"],
            tokenizer=self.retrieval_models[f"{model_name}_tokenizer"],
        )
                
        vector = embed.tolist()[0]
        payload = {"query": "{!knn f=vector topK=5}" + str(vector)}
        response = requests.post(solr_url, json=payload).json()
                
        # Extract required field from Solr `response`
        retrieved_docs = response["response"]["docs"]
        all_docs = [
            [res_["text"], res_["score"], res_["url"], core_name]
            for res_ in retrieved_docs
        ]

        # Truncate the retrieved `text` to character limit
        for i in range(len(all_docs)):
            if all_docs[i][0] and len(all_docs[i][0]) > char_limit:  
                all_docs[i][0] = all_docs[i][0][:char_limit]
                
        print(f"Retrieved all docs from {solr_url} using {model_name} embeddings.")
        return all_docs

    def get_response(self, query, core_name):
        # Combine the two retrieval results
        retrieved_docs = []

        # Search for relevant context using all available retrieval models
        for model_name in self.retrieval_model_names:
            print(f"Embedding query using {model_name}...")

            # Search for context in all cores for current retrieval model          
            solr_url = (
                "http://localhost:8983/solr/"
                + core_name
                + "/select?fl=text,score,url"
            )
            
            retrieved_docs += self.retrieve_context(
                query, core_name, solr_url, model_name
            )
                
            print(f"Retrieved all relevant docs using {model_name}.\n")
        

        print(f"Total {len(retrieved_docs)} docs retrieved from solr cores.")
        # Retain only top 3 results by score and extract the text only
        reranked_retrieved_docs = sorted(
            retrieved_docs, key=lambda x: x[2], reverse=True
        )[: self.retrieval_top_k]
        
    
        # Check total token size of all retrieved_docs
        context_size = sum(len(doc[0]) for doc in reranked_retrieved_docs)
        print(f"Re-ranked retrieved context contains {context_size} chars or  ~{int(context_size/4)} tokens.")

        # Check the top score of the retrieved docs
        top_ret_score = reranked_retrieved_docs[0][1]
        
        if top_ret_score < self.retrieval_threshold:
            # Do not use any context from the retrieval
            retrieved_text = []
            print(f"Retrieved score is {top_ret_score}, which is less than {self.retrieval_threshold}. Dropping retrieved context.")

        else:
            retrieved_text = [(res_[0], res_[2][0]) for res_ in reranked_retrieved_docs]

        return retrieved_text

def main(): 
    args = parse_args()
    input_sen = args["input_sen"]
    core_name = args["core_name"]

    solr = SolrRetriever()
    response = solr.get_response(input_sen, core_name)
    print(f"Total number of responses retrived: {len(response)}")
    print(f"Retrieval result:\n{response}") 


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_sen",
        default=str("Avenger Infinity wars movie review"),
        type=str,
        help="Input the query sentence"
    )
    parser.add_argument(
        "--core_name",
        type=str,
        help="give the core name",
        required=True
    )
    return vars(parser.parse_args())


if __name__ == "__main__":
    main()

