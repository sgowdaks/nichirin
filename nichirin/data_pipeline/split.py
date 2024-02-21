import csv
import re
import argparse
import hashlib
import nltk
import sys
import pandas as pd

from pathlib import Path

nltk.download('punkt')

def parse_tsv(file):
    with open(file, 'r') as data:
        for line in data:
            key =  hashlib.sha256(str(line).encode()).hexdigest()
            values = line.split("\t")
            yield values, key

def split_paragraph(paragraph):
    # sentences = re.split(r'(?<=[.!?])\s+', paragraph)
    result = []
    start = 0
    par = len(paragraph.split())

    if par < 750:
        result.append(paragraph)
        return result

    paragraph = paragraph.split()

    while start < par:
        if start + 750 > par:
            result.append(" ".join(paragraph[start:par]))
            return result
        result.append(" ".join(paragraph[start : start + 750]))  # 1st type
        start += 700

    result.append(" ".join(paragraph[start - par : par]))
    return result

             
def join_sentences(sentences, n):
    # Join n sentences at a time
    joined_sentences = [' '.join(sentences[i : i + n]) for i in range(0, len(sentences), n)]
    return joined_sentences

def split_data(files_path):
    path = Path(files_path)
    clean_files = [f for f in path.glob('*.tsv')]
        
    all_the_files = [d for d in path.iterdir()]
    
    for clean_file in clean_files:
        if Path(str(clean_file) + ".split") not in all_the_files:
            with open(str(clean_file) + ".split", 'w') as output_file:
                tsv_writer = csv.writer(output_file, delimiter='\t')
                                     
                for row, key in parse_tsv(clean_file):
                    try:
                        title, sen, url = list(row)
                    
                        url = url.replace("\n", "")
                                                
                        result = split_paragraph(sen)   
                        
                        for i, sen in enumerate(result):                                                      
                            sen = title + ":" + sen.replace('\n', '')                       
                            tsv_writer.writerow([sen, url, key])
                    except:
                        print(f"skipping the line {list(row)}")
                        

