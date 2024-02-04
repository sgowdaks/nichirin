import csv
import re
import argparse
import hashlib
import nltk
import sys
import pandas as pd

from pathlib import Path
from retriever.solr_index_docs import SolrIndex

nltk.download('punkt')

def parse_tsv(file):
    with open(file, 'r') as data:
        # for line in f:
        for line in data:
            values = line.split("\t")
            yield values

def split_paragraph(paragraph):
    # sentences = re.split(r'(?<=[.!?])\s+', paragraph)
    result = []
    start = 0
    par = len(paragraph.split())

    if par < 500:
        result.append(paragraph)
        return result

    paragraph = paragraph.split()

    while start < par:
        print(start, start + 500)
        if start + 500 > par:
            result.append(" ".join(paragraph[start:par]))
            return result
        result.append(" ".join(paragraph[start : start + 500]))  # 1st type
        start += 250

    result.append(" ".join(paragraph[start - par : par]))
    return result

             
def join_sentences(sentences, n):
    # Join n sentences at a time
    joined_sentences = [' '.join(sentences[i : i + n]) for i in range(0, len(sentences), n)]
    return joined_sentences

def add_sha_tocleanfiles(clean_files):
    
    for file in clean_files:    
        df = pd.read_csv(file, sep='\t')
        df['hash'] = df.apply(lambda x: hashlib.sha256(str(x.values).encode()).hexdigest(), axis=1)
        df.to_csv(file, sep='\t', index=False)



def split(files_path):
    path = Path(files_path)
    clean_files = [f for f in path.glob('*.tsv')]
    
    #add sha256 to the existing tsv files
    add_sha_tocleanfiles(clean_files)
    
    all_the_files = [d for d in path.iterdir()]
    
    for clean_file in clean_files:
        if Path(str(clean_file) + ".split") not in all_the_files:
            with open(str(clean_file) + ".split", 'w') as output_file:
                tsv_writer = csv.writer(output_file, delimiter='\t')
                row = parse_tsv(clean_file)
                
                key = row[-1]
                
                for value in row[:-1]:
                    
                    result = split_paragraph(value)   
                     
                    for i, sen in enumerate(result):                                                      
                        sen = sen.strip("\n")
                        tsv_writer.writerow([key, sen])
                        

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input',
        type=Path,
        required=True,
        help='give the input file path',
    )
    parser.add_argument(
        '--core',
        type=str,
        required=True,
        help='give the core name',
    )
    args = parser.parse_args()
    return vars(args)


if __name__ == '__main__':
    args = parse_args()
    split(args['input'])
    si = SolrIndex(args["input"], args["core"])
    si.read_()