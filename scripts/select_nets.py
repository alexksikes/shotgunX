import sys, re, os

p = re.compile('''Ranker_No_Doubles
Ranker_No_Body
Ranker_No_Number
Ranker_Only_Number
Ranker_No_Click
Ranker_Only_Boost
Ranker_Only_ExperimentalClickBoost
Ranker_Only_NumberOfOccurrences
Ranker_Only_Segment
Ranker_Only_First
Ranker_Only_Url
Ranker_Only_GlobalToolbarClickBoost
Ranker_Only_Query
Ranker_Only_Anchor
Ranker_Only_Top
Ranker_Only_Body
Ranker_Only_Near
Ranker_Only_Span
Ranker_Only_Spans
Ranker_Only_Title
Ranker_Only_Doubles
Ranker_Only_Order
Ranker_Only_Short
Ranker_Only_Attribute'''.replace('\n', '\.|'))

def run(dir, out_dir):
    for f in os.listdir(dir):
        if p.match(f):      
            print 'copying %s' % f
            os.system('cp %s %s' % (os.path.join(dir, f), 
                os.path.join(out_dir, f)))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: python select_nets.py dir in_dir out_dir"
    else:
        run(sys.argv[1], sys.argv[2])
