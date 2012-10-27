import sys

from model_library import get_simplified_dataset

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: python extract_judgements.py dataset_path"
    else:
        get_simplified_dataset(sys.argv[1])