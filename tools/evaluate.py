import sys, os

neural_path = ''

def main(trained_models, predictions_out, dataset):
    cmd = '%s %s %s %s 100000 /OutputDocRanking' % (neural_path, trained_models, predictions_out, dataset)
    print cmd
    os.system(cmd)
        
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: python evaluate_models.py trained_models_path predictions_out_path dataset_path"
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])