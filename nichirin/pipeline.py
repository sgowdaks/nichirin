#input should be specific
import argparse

from pathlib import Path
from .data_pipeline.generate_embeddings import GenerateEmbeddings
from .data_pipeline.split import split_data
from .utils.data_utils import load_yaml

def main():
    args = parse_args()
    data_path = args['path']
    
    conf_path = Path(__file__).parent / "confs/app.yaml"
    
    assert conf_path.exists(), f"{conf_path.resolve()} does not exist"
    
    cfg = load_yaml(conf_path)
    split_data(data_path)
    
    model_id = cfg['retrieval']['gte-large']['model_id']
    
    create_embeddings = GenerateEmbeddings(model_id)
    create_embeddings.embeddings(data_path)

        
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="Give the path to data", required=True)
    args = parser.parse_args()
    return vars(args)

if __name__ == "__main__":
    main()

