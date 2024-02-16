import os
import argparse
import subprocess

from pathlib import Path


def partition(file_path):

    if not Path(file_path).is_file():
        print("File not found!")
        exit(1)
        
    output_dir = Path(file_path) / "output_dir"
    
    os.makedirs(output_dir)
      
    file_size = Path(file_path).stat().st_size

    print(f"Size of {file_path} is {file_size} bytes.")
    
    #if file size is lesser than 1GB then don't partition
    if file_size < 1000000000:
        subprocess.run(["mv", file_path, output_dir], check=True)

    with open(file_path, 'rb') as f:       
        i = 0
        chunk = f.read(1000000000)  # read 1 GB at a time
        while chunk:
            with open(os.path.join(output_dir, f"part-{i:02}.tsv"), 'wb') as f_part:
                f_part.write(chunk)
            i += 1
            chunk = f.read(1000000000)

    print("Partitioning completed. Files are named as part-00, part-01, etc.")

    # Remove the original file
    os.remove(file_path)

    print("Original file removed.")

def main(path): 
    SOLR_VERSION = os.getenv('SOLR_VERSION', "9.4.0")
    partition(SOLR_VERSION, path)
    
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="Give the path to data", required=True)
    args = parser.parse_args()
    return vars(args)

if __name__ == "__main__":
    args = parse_args()
    main(args["path"])
