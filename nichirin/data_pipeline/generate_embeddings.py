import torch
import pandas as pd
import numpy as np
import argparse
import csv

from tqdm.auto import tqdm
from pathlib import Path
from transformers import AutoTokenizer, AutoModel


class GenerateEmbeddings:
    def __init__(self, model_id):
        self.model_id = model_id
        self.device = "cuda"
        self.model = AutoModel.from_pretrained(self.model_id).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.model = self.model.eval()

    def mean_pooling(self, token_embeddings, mask):
        token_embeddings = token_embeddings.masked_fill(~mask[..., None].bool(), 0.0)
        sentence_embeddings = token_embeddings.sum(dim=1) / mask.sum(dim=1)[..., None]
        return sentence_embeddings

    def get_embeddings(self, text_list):
        inputs = self.tokenizer(text_list, padding=True, truncation=True, max_length=512, return_tensors='pt').to(self.device)
        outputs = self.model(**inputs)
        embeddings = self.mean_pooling(outputs[0], inputs['attention_mask'])
        return embeddings

    def embeddings(self, inp_file):
        torch.set_grad_enabled(False)
        print("Loading data from ", inp_file)

        path = Path(inp_file)
        tsv_files = [f for f in path.glob('*.split')]
        all_the_files = [d for d in path.iterdir()]

        embeddings = []

        for tsv_file in tsv_files:
            if Path(str(tsv_file) + ".pt") not in all_the_files:
                # with open(str(tsv_file) + ".tok", 'w') as output_file:
                    with open(tsv_file, encoding='utf-8', errors='ignore') as lines:

                        dataset = [x for x in lines if x]  # drop empty lines
                        print(f"Num lines {len(dataset)}")
                        
                        current_group = []
                        embeddings = []
                        
                        for i, line in enumerate(dataset):   
                            sen, url, hash = line.split("\t")    
                            sen = sen.replace("\n", "")             
                            if i % 100 == 0 and current_group:
                                embedding = self.get_embeddings(current_group)
                                embeddings.append(embedding.detach().cpu())
                                current_group = [sen]
                            else:
                                current_group.append(sen)
                                
                        if current_group:
                            embedding = self.get_embeddings(current_group)
                            embeddings.append(embedding.detach().cpu())

                        tensor = torch.cat(embeddings)
                        embeddings = []
                        torch.save(tensor, str(tsv_file) + '.pt')

