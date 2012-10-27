import sys

from model_library import make_splits

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: python make_splits_random.py predictions_dir split_percent split_names out_dir"
    else:
        make_splits(sys.argv[1], map(int, sys.argv[2].split(',')), sys.argv[3].split(','), sys.argv[4])
