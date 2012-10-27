import sys, os

def run(in_dir, out_dir, num_splits):
    sp_number = 0
    num_files_per_split = len(os.listdir(in_dir)) / num_splits
    
    for i, f in enumerate(os.listdir(in_dir)):
        if i % num_files_per_split == 0:
            out_split = os.path.join(out_dir, str(sp_number))
            try: os.makedirs(out_split)
            except: pass
            sp_number +=1 
        
        cmd = 'cp %s %s' % (os.path.join(in_dir, f), os.path.join(out_split, f))
        print cmd
        os.system(cmd)
        
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: python split_directory.py in_dir out_dir number_of_splits"
    else:
        run(sys.argv[1], sys.argv[2], int(sys.argv[3]) - 1)