#input should be specific
import argparse

from nichirin.data_pipeline.generate_embeddings import GenerateEmbeddings
from nichirin.data_pipeline.split import split_data


def main(path):
    
    split_data()
    
    create_embeddings = GenerateEmbeddings()
    create_embeddings.embeddings()

        
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="Give the path to data", required=True)
    args = parser.parse_args()
    return vars(args)

if __name__ == "__main__":
    args = parse_args()
    main(args["path"])

