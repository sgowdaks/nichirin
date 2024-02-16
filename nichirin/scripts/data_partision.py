import os
import argparse

from pathlib import Path


def partition():

    file_path = input("Enter the file path: ")

    if not Path(file_path).is_file():
        print("File not found!")
        exit(1)

    file_size = Path(file_path).stat().st_size

    print(f"Size of {file_path} is {file_size} bytes.")

    with open(file_path, 'rb') as f:
        i = 0
        while chunk := f.read(1024):
            with open(f"part-{i:02}", 'wb') as f_part:
                f_part.write(chunk)
            i += 1

    print("Partitioning completed. Files are named as part-00, part-01, etc.")

    # Remove the original file
    os.remove(file_path)

    print("Original file removed.")

def main(path): 
    SOLR_VERSION = os.getenv('SOLR_VERSION', "9.4.0")
    partition(SOLR_VERSION)
    
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="Give the path to data", required=True)
    args = parser.parse_args()
    return vars(args)

if __name__ == "__main__":
    args = parse_args()
    main(args["path"])
