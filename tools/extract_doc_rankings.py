import sys

from model_library import build_model_library

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: python extract_doc_rankings.py doc_rankings_dir dataset_path out_dir"
    else:
        build_model_library(sys.argv[1], sys.argv[2], sys.argv[3])