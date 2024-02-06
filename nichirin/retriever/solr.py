import torch
import argparse
import requests
from typing import List
from datetime import date
from transformers import AutoTokenizer, AutoModel

from nichirin.utils.data_utils import load_yaml
import logging

# Use GPU if available else revert to CPU
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class SolrRetriever:
    def __init__(self, logger=None, cfg=None) -> None:
        if not cfg:
            cfg = load_yaml("confs/app.yaml")

        self.cfg = cfg
        self.logger = logging.getLogger(__name__)
        self.retrieval_conf = self.cfg["retrieval"]
        self.retrieval_threshold = self.cfg["retrieval_threshold"]
        self.retrieval_top_k = self.cfg["retrieval_top_k"]

        # Load all available retrieval models separately
        self.retrieval_models = self.load_retrieval_models()
        self.logger.info("Retrieval setup complete!\n")

    def load_retrieval_models(self) -> dict:
        self.retrieval_model_names = list(self.retrieval_conf.keys())
        if self.logger:
            self.logger.info(
                f"Using {len(self.retrieval_model_names)} models for retrieval - {self.retrieval_model_names}"
            )

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
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = model.eval()
        torch.set_grad_enabled(False)
        if self.logger:
            self.logger.info(f"Model and tokenizer for {model_id} loaded.")
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
            [res_["text"], res_["url"], res_["score"], core_name]
            for res_ in retrieved_docs
        ]

        # Truncate the retrieved `text` to character limit
        for i in range(len(all_docs)):
            if all_docs[i][0] and len(all_docs[i][0]) > char_limit:
                self.logger.info(
                    f"Current retrieved text length from {core_name} = {len(all_docs[i][0])} chars. Truncating to {char_limit} chars."
                )
                all_docs[i][0] = all_docs[i][0][:char_limit]

        self.logger.info(
            f"Retrieved all docs from {solr_url} using {model_name} embeddings."
        )
        return all_docs

    def get_sources(self, retrieved_docs):
        # Retrieved docs schema: text, url, score, core_name
        source_urls = [doc[1] for doc in retrieved_docs]
        source_names = [doc[3] for doc in retrieved_docs]

        for src_url, src_name in zip(source_urls, source_names):
            if "wiki" in src_name:
                updated_url = src_url.replace(" ", "_")
                source_urls[source_urls.index(src_url)] = updated_url

        # Remove duplicate sources
        source_urls = list(set(source_urls))
        self.logger.info(f"Top retrieval sources: {source_urls}")
        return source_urls

    def get_response(self, query):
        # Combine the two retrieval results
        retrieved_docs = []

        # Search for relevant context using all available retrieval models
        for model_name in self.retrieval_model_names:
            self.logger.info(f"Embedding query using {model_name}...")

            # Search for context in all cores for current retrieval model
            for core_name in self.retrieval_conf[model_name]["cores"]:
                solr_url = (
                    "http://localhost:8983/solr/"
                    + core_name
                    + "/select?fl=id,text,score,url"
                )
                # TODO: Run this method for all cores concurrently
                retrieved_docs += self.retrieve_context(
                    query, core_name, solr_url, model_name
                )
            self.logger.info(f"Retrieved all relevant docs using {model_name}.\n")

        self.logger.info(
            f"Total {len(retrieved_docs)} docs retrieved from all solr cores."
        )
        # Retain only top 3 results by score and extract the text only
        reranked_retrieved_docs = sorted(
            retrieved_docs, key=lambda x: x[2], reverse=True
        )[: self.retrieval_top_k]

        # Check total token size of all retrieved_docs
        context_size = sum(len(doc[0]) for doc in reranked_retrieved_docs)
        self.logger.info(
            f"Re-ranked retrieved context contains {context_size} chars or  ~{int(context_size/4)} tokens."
        )

        # Check the top score of the retrieved docs
        top_ret_score = reranked_retrieved_docs[0][2]

        if top_ret_score < self.retrieval_threshold:
            # Do not use any context from the retrieval
            retrieved_text, top_retrieved_sources = [], []
            self.logger.info(
                f"Retrieved score is {top_ret_score}, which is less than {self.retrieval_threshold}. Dropping retrieved context."
            )

        else:
            self.logger.info(
                f"Re-ranked Retrieval docs with top score = {top_ret_score}: {reranked_retrieved_docs}"
            )
            top_retrieved_sources = self.get_sources(reranked_retrieved_docs)
            # Extract only text from the retrieved docs
            retrieved_text = [res_[0] for res_ in reranked_retrieved_docs]

        return retrieved_text, top_retrieved_sources


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_sen",
        default=str("Avenger Infinity wars movie review"),
        type=str,
        help="Input the query sentence",
    )
    return vars(parser.parse_args())


if __name__ == "__main__":
    args = parse_args()
    input_sen = args["input_sen"]

    solr = SolrRetriever()
    response, sources = solr.get_response(input_sen)
    print(f"Retrieval result:\n{response}\nReferences:\n{sources}")
