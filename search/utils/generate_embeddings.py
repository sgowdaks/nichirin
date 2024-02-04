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
            if Path(str(tsv_file) + ".tok") not in all_the_files:
                with open(str(tsv_file) + ".tok", 'w') as output_file:
                    with open(tsv_file, encoding='utf-8', errors='ignore') as lines:
                        tsv_writer = csv.writer(output_file, delimiter='\t')

                        dataset = [x for x in lines if x]  # drop empty lines
                        print(f"Num lines {len(dataset)}")

                        count = 0
                        sentences_with_id = []
                        for i, sentence in enumerate(dataset):
                            try:
                                key, sen = sentence.split('\t')
                            except ValueError as e:
                                count += 1
                                continue
                            sentences_with_id.append((i, len(sen.split()), sen, url, key, id))

                        print("count ", count)
                        sorted_sentences = sorted(sentences_with_id, key=lambda x: x[1])

                        max_diff = 10
                        current_group = []
                        prev_count = 0
                        for id, word_count, sentence, url, key, id_ in tqdm(sorted_sentences):
                            if len(sentence.split(" ")) < 20:
                                continue
                            if not current_group:
                                prev_count = word_count
                                current_group.append(sentence)
                            else:
                                if word_count - prev_count <= max_diff and len(current_group) < 300:
                                    prev_count = word_count
                                    current_group.append(sentence)
                                else:
                                    embedding = self.get_embeddings(current_group)
                                    embeddings.append(embedding.detach().cpu())
                                    current_group = [sentence]
                                    prev_count = word_count
                            tsv_writer.writerow([id, sentence, url, key, id_.strip("\n")])

                        if current_group:
                            embedding = self.get_embeddings(current_group)
                            embeddings.append(embedding.detach().cpu())

                        tensor = torch.cat(embeddings)
                        embeddings = []
                        torch.save(tensor, str(tsv_file) + '.pt')


def main(args):
    inp_file = args['data_dir']
    model_id = args['model_path']

    ge = GenerateEmbeddings(model_id)
    ge.embeddings(inp_file)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--data-dir',
        required=True,
        type=Path,
        help='give the path of the data directory',
    )
    parser.add_argument(
        '--model-path', default="facebook/contriever", type=str, help='give the model path/name from hugging face'
    )
    args = parser.parse_args()
    return vars(args)


if __name__ == '__main__':
    main(parse_args())