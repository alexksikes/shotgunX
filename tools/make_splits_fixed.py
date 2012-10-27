import sys

from model_library import make_splits_fixed

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: python make_splits_fixed.py predictions_dir split_sizes split_names out_dir"
    else:
        make_splits_fixed(sys.argv[1], sys.argv[2], sys.argv[3])