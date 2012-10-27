import sys, re, os

def fix_filename(f):
    return re.sub('\-(Test|1000|Validation|Training)', '', f)

def run(dir):
    for f in os.listdir(dir):
        f = os.path.join(dir, f)
        new_f = fix_filename(f)
        
        os.system('mv %s %s' % (f, new_f))
        
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: python fix_filenames.py dir"
    else:
        run(sys.argv[1])